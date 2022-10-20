package server

import (
	"errors"
	"fmt"
	"io/fs"
	"os"

	"github.com/labstack/echo/v4"
	"github.com/myOmikron/echotools/color"
	"github.com/myOmikron/echotools/execution"
	"github.com/myOmikron/echotools/worker"
	"github.com/pelletier/go-toml"

	"github.com/myOmikron/bnv-manager/models/config"
	"github.com/myOmikron/bnv-manager/modules/wp"
)

func StartServer(configPath string) {
	conf := &config.Config{}

	if configBytes, err := os.ReadFile(configPath); errors.Is(err, fs.ErrNotExist) {
		color.Printf(color.RED, "Config was not found at %s\n", configPath)
		b, _ := toml.Marshal(conf)
		fmt.Print(string(b))
		os.Exit(1)
	} else {
		if err := toml.Unmarshal(configBytes, conf); err != nil {
			panic(err)
		}
	}

	// Check for valid config values
	if err := conf.CheckConfig(); err != nil {
		fmt.Println(err.Error())
		os.Exit(1)
	}

	db := initializeDB(conf)

	readOnlyWP := worker.NewPool(&worker.PoolConfig{
		NumWorker: 20,
		QueueSize: 20,
	})

	adminWP := worker.NewPool(&worker.PoolConfig{
		NumWorker: 20,
		QueueSize: 20,
	})

	color.Print(color.PURPLE, "Starting read only ldap worker ... ")
	if err := readOnlyWP.StartWithWorkerCreator(wp.StartROWorker(conf)); err != nil {
		panic(err)
	}
	color.Println(color.GREEN, "Done")

	color.Print(color.PURPLE, "Starting admin ldap worker ... ")
	if err := adminWP.StartWithWorkerCreator(wp.StartAdminWorker(conf)); err != nil {
		panic(err)
	}
	color.Println(color.GREEN, "Done")

	e := echo.New()
	e.HideBanner = true
	e.HidePort = true

	initializeMiddleware(e, db, conf)

	defineRoutes(e, db, conf, readOnlyWP, adminWP)

	color.Print(color.PURPLE, fmt.Sprintf("Starting listening on http://%s\n", conf.GetListenString()))
	execution.SignalStart(e, conf.GetListenString(), &execution.Config{
		ReloadFunc: func() {
			readOnlyWP.Stop()
			adminWP.Stop()
			StartServer(configPath)
		},
		StopFunc: func() {
			readOnlyWP.Stop()
			adminWP.Stop()
		},
		TerminateFunc: func() {
			readOnlyWP.Stop()
			adminWP.Stop()
		},
	})
}

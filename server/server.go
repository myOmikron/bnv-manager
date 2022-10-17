package server

import (
	"errors"
	"fmt"
	"io/fs"
	"os"

	"github.com/labstack/echo/v4"
	"github.com/myOmikron/echotools/color"
	"github.com/myOmikron/echotools/execution"
	"github.com/pelletier/go-toml"

	"github.com/myOmikron/bnv-manager/models/config"
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

	e := echo.New()
	e.HideBanner = true
	e.HidePort = true

	initializeMiddleware(e, db, conf)

	defineRoutes(e, db, conf)

	color.Print(color.PURPLE, "Starting listening on "+fmt.Sprintf("http://%s\n", conf.GetListenString()))
	execution.SignalStart(e, conf.GetListenString(), &execution.Config{
		ReloadFunc: func() {
			StartServer(configPath)
		},
		StopFunc: func() {

		},
		TerminateFunc: func() {

		},
	})
}

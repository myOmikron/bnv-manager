package main

import (
	"fmt"
	"github.com/hellflame/argparse"

	"github.com/myOmikron/bnv-manager/server"
)

func main() {
	parser := argparse.NewParser("bnv-manager", "", &argparse.ParserConfig{
		DisableDefaultShowHelp: true,
	})

	configPath := parser.String("", "config-path", &argparse.Option{Default: "/etc/bnv-manager/config.toml"})

	if err := parser.Parse(nil); err != nil {
		fmt.Println(err.Error())
		return
	}

	server.StartServer(*configPath)
}

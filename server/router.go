package server

import (
	"github.com/labstack/echo/v4"
	"gorm.io/gorm"

	"github.com/myOmikron/bnv-manager/models/config"
)

func defineRoutes(e *echo.Echo, db *gorm.DB, conf *config.Config) {
	e.Static("/", "static/")
}

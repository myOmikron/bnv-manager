package server

import (
	"github.com/labstack/echo/v4"
	"github.com/myOmikron/echotools/middleware"
	"gorm.io/gorm"

	"github.com/myOmikron/bnv-manager/handler"
	"github.com/myOmikron/bnv-manager/models/config"
)

func loginRequired(f echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		sessionContext, err := middleware.GetSessionContext(c)
		if err != nil {
			return c.String(500, "Internal server error")
		}

		if sessionContext.IsAuthenticated() {
			return f(c)
		} else {
			return c.String(401, "Authentication is required")
		}
	}
}

func defineRoutes(e *echo.Echo, db *gorm.DB, conf *config.Config) {
	api := handler.Wrapper{
		DB:     db,
		Config: conf,
	}

	e.POST("/api/login", api.Login)
	e.GET("/api/logout", api.Logout)
	
	e.GET("/api/me", loginRequired(api.Me))

	e.Static("/", "static/")
}

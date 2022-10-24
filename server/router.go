package server

import (
	"github.com/labstack/echo/v4"
	mw "github.com/myOmikron/echotools/middleware"
	"github.com/myOmikron/echotools/worker"
	"gorm.io/gorm"

	"github.com/myOmikron/bnv-manager/handler"
	"github.com/myOmikron/bnv-manager/models/config"
	"github.com/myOmikron/bnv-manager/models/dbmodels"
)

func loginRequired(f echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		sessionContext, err := mw.GetSessionContext(c)
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

func adminRequired(f echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		sessionContext, err := mw.GetSessionContext(c)
		if err != nil {
			c.Logger().Error(err)
			return c.String(500, "Internal server error")
		}

		if !sessionContext.IsAuthenticated() {
			return c.String(401, "Authentication is required")
		}

		switch u := sessionContext.GetUser().(type) {
		case *dbmodels.User:
			if u.IsAdmin {
				return f(c)
			} else {
				return c.NoContent(403)
			}
		default:
			return c.String(500, "Internal server error")
		}
	}
}

func defineRoutes(e *echo.Echo, db *gorm.DB, conf *config.Config, readOnlyWP worker.Pool, adminWP worker.Pool) {
	api := handler.Wrapper{
		DB:         db,
		Config:     conf,
		ReadOnlyWP: readOnlyWP,
		AdminWP:    adminWP,
	}

	e.POST("/api/login", api.Login)
	e.GET("/api/logout", api.Logout)
	e.POST("/api/logout", api.Logout)

	e.GET("/api/me", loginRequired(api.Me))
	e.PUT("/api/me/password", loginRequired(api.ChangePassword))

	e.POST("/api/clubadmins", adminRequired(api.CreateClubAdmin))
	e.GET("/api/clubadmins", adminRequired(api.GetClubAdmins))

	e.PUT("/api/clubadmins/:id/password", adminRequired(api.ResetPasswordClubAdmin))

	e.GET("/api/clubs", adminRequired(api.GetClubs))
	e.POST("/api/clubs", adminRequired(api.CreateClub))
	e.DELETE("/api/clubs", adminRequired(api.DeleteClub))
	e.GET("/api/clubs/:id", adminRequired(api.GetClub))

	e.GET("/api/domains", adminRequired(api.GetDomains))

	e.Static("/", "static/")
}

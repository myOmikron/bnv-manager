package server

import (
	"net/url"

	"github.com/labstack/echo/v4"
	emw "github.com/labstack/echo/v4/middleware"
	mw "github.com/myOmikron/echotools/middleware"
	"gorm.io/gorm"

	"github.com/myOmikron/bnv-manager/models/config"
	"github.com/myOmikron/bnv-manager/models/dbmodels"
)

func initializeMiddleware(e *echo.Echo, db *gorm.DB, conf *config.Config) {
	e.Use(emw.Recover())

	logFormat := "${remote_ip} - - [${time_custom}] \"${method} ${path} ${protocol}\" ${status} ${bytes_out}\n"
	customTimeFormat := "2/Jan/2006:15:04:05 -0700"
	e.Use(emw.LoggerWithConfig(emw.LoggerConfig{
		Format:           logFormat,
		CustomTimeFormat: customTimeFormat,
	}))

	// Security unpacking
	allowedHosts := &mw.SecurityConfig{
		AllowedHosts:            []mw.AllowedHost{},
		UseForwardedProtoHeader: conf.Server.UseForwardedProtoHeader,
	}
	for _, allowedHost := range conf.Server.AllowedHosts {
		u, _ := url.Parse(allowedHost)
		https := false
		if u.Scheme == "https" {
			https = true
		}
		allowedHosts.AllowedHosts = append(allowedHosts.AllowedHosts, mw.AllowedHost{
			Host:  u.Host,
			Https: https,
		})
	}
	e.Use(mw.Security(allowedHosts))

	e.Use(emw.BodyLimit("5MB"))

	e.Use(mw.Session(db, &mw.SessionConfig{
		CookieName: "sessionid",
	}))

	mw.RegisterAuthProvider(func() (string, func(foreignKey uint) any) {
		return "bnv_ldap", func(foreignKey uint) any {
			var user dbmodels.User

			var count int64
			db.Find(&user, "ID = ?", foreignKey).Count(&count)

			if count != 1 {
				return nil
			}

			return &user
		}
	})
}

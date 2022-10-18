package handler

import (
	"github.com/labstack/echo/v4"
	"github.com/myOmikron/echotools/middleware"

	"github.com/myOmikron/bnv-manager/models/dbmodels"
)

type meResponse struct {
	IsAdmin     bool   `json:"is_admin"`
	IsClubAdmin bool   `json:"is_club_admin"`
	Username    string `json:"username"`
}

func (w *Wrapper) Me(c echo.Context) error {
	sessionContext, err := middleware.GetSessionContext(c)
	if err != nil {
		return c.String(500, "Internal server error")
	}

	user := sessionContext.GetUser()
	switch u := user.(type) {
	case *dbmodels.User:
		return c.JSON(200, meResponse{
			IsAdmin:     u.IsAdmin,
			IsClubAdmin: u.IsClubAdmin,
			Username:    u.Username,
		})
	default:
		return c.String(500, "Internal server error")
	}
}

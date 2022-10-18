package handler

import (
	"github.com/labstack/echo/v4"
	"github.com/myOmikron/echotools/middleware"
)

func (w *Wrapper) Logout(c echo.Context) error {
	if err := middleware.Logout(w.DB, c); err != nil {
		c.Logger().Error(err)
		return c.String(500, "Internal server error")
	}
	return c.NoContent(200)
}

package handler

import (
	"github.com/labstack/echo/v4"

	"github.com/myOmikron/bnv-manager/modules/mailcow_impl"
)

type getDomainsResponse struct {
	Domains []string `json:"domains"`
}

func (w *Wrapper) GetDomains(c echo.Context) error {
	domains, err := mailcow_impl.GetDomains(w.Config)
	if err != nil {
		c.Logger().Error(err)
		return c.String(500, "Mailcow Error")
	}

	return c.JSON(200, getDomainsResponse{
		Domains: domains,
	})
}

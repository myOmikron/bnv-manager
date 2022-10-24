package handler

import (
	"github.com/labstack/echo/v4"
	"github.com/myOmikron/bnv-manager/modules/ldap_impl"
)

type getClubPath struct {
	ID string `param:"id"`
}

type getClubResponse struct {
	ClubName string   `json:"name"`
	Domains  []string `json:"domains"`
}

func (w *Wrapper) GetClub(c echo.Context) error {
	path := getClubPath{}

	if err := c.Bind(&path); err != nil {
		return c.String(400, "Bad request")
	}

	if path.ID == "" {
		return c.String(400, "Bad request")
	}

	cl, err := ldap_impl.GetClubByID(path.ID, w.Config, w.ReadOnlyWP)
	if err != nil {
		return c.String(500, "LDAP Error")
	}

	return c.JSON(200, getClubResponse{
		ClubName: cl.Description,
		Domains:  cl.Domains,
	})
}

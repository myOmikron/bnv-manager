package handler

import (
	"github.com/labstack/echo/v4"

	"github.com/myOmikron/bnv-manager/modules/ldap_impl"
)

type club struct {
	ClubID   string   `json:"club_id"`
	ClubName string   `json:"club_name"`
	Domains  []string `json:"domains"`
}

type getClubsResponse struct {
	Clubs []club `json:"clubs"`
}

func (w *Wrapper) GetClubs(c echo.Context) error {
	clubs, err := ldap_impl.GetAllClubs(w.Config, w.ReadOnlyWP)
	if err != nil {
		c.Logger().Error(err)
		return c.String(500, "LDAP Error")
	}

	res := getClubsResponse{Clubs: make([]club, 0)}
	for _, cl := range clubs {
		res.Clubs = append(res.Clubs, club{
			ClubID:   cl.CN,
			ClubName: cl.Description,
			Domains:  cl.Domains,
		})
	}

	return c.JSON(200, res)
}

package handler

import (
	"github.com/labstack/echo/v4"

	"github.com/myOmikron/bnv-manager/modules/ldap_impl"
)

type club struct {
	ClubID   string `json:"club_id"`
	ClubName string `json:"club_name"`
}

type getClubsResponse struct {
	Clubs []club `json:"clubs"`
}

func (w *Wrapper) GetClubs(c echo.Context) error {
	clubs, err := ldap_impl.GetAllClubs(w.Config)
	if err != nil {
		c.Logger().Error(err)
		return c.String(500, "LDAP Error")
	}

	res := getClubsResponse{Clubs: make([]club, 0)}
	for _, c := range clubs {
		res.Clubs = append(res.Clubs, club{
			ClubID:   c.CN,
			ClubName: c.Description,
		})
	}

	return c.JSON(200, res)
}

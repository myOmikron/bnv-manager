package handler

import (
	"github.com/labstack/echo/v4"
	"github.com/myOmikron/echotools/utility"

	"github.com/myOmikron/bnv-manager/modules/ldap_impl"
)

type createClubAdminRequest struct {
	Firstname *string `json:"firstname" echotools:"required;not empty"`
	Surname   *string `json:"surname" echotools:"required;not empty"`
	Password  *string `json:"password" echotools:"required;not empty"`
	ClubID    *string `json:"club_id" echotools:"required;not empty"`
}

type createClubAdminResponse struct {
	Username string `json:"username"`
}

func (w *Wrapper) CreateClubAdmin(c echo.Context) error {
	var form createClubAdminRequest

	if err := utility.ValidateJsonForm(c, &form); err != nil {
		return c.String(400, err.Error())
	}

	groupDN, err := ldap_impl.CheckIfClubExists(*form.ClubID, w.Config, w.ReadOnlyWP)
	if err != nil {
		c.Logger().Error(err)
		return c.String(500, "LDAP Error")
	}

	if groupDN == nil {
		return c.String(400, "Club does not exist")
	}

	username, err := ldap_impl.GenerateUsername(*form.Firstname, *form.Surname, w.Config, w.ReadOnlyWP)
	if err != nil {
		c.Logger().Error(err)
		return c.String(500, "LDAP Error")
	}
	dn, err := ldap_impl.CreateUser(
		*username,
		*form.Firstname,
		*form.Surname,
		*form.Password,
		nil,
		w.Config,
		w.AdminWP,
	)
	if err != nil {
		c.Logger().Error(err)
		return c.String(500, "LDAP Error")
	}

	if err := ldap_impl.AddDNToGroup(*dn, *groupDN, w.AdminWP); err != nil {
		c.Logger().Error(err)
		return c.String(500, "LDAP Error")
	}

	if err := ldap_impl.AddDNToGroup(*dn, w.Config.LDAP.ClubAdminGroupDN, w.AdminWP); err != nil {
		c.Logger().Error(err)
		return c.String(500, "LDAP Error")
	}

	return c.JSON(201, createClubAdminResponse{
		Username: *username,
	})
}

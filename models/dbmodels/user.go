package dbmodels

import (
	"time"

	"github.com/labstack/echo/v4"
	"github.com/myOmikron/echotools/utilitymodels"
	"gorm.io/gorm"
)

type User struct {
	utilitymodels.Common
	DN          string `gorm:"unique"`
	IsClubAdmin bool   `gorm:"not null"`
	IsAdmin     bool   `gorm:"not null"`
}

func (u *User) GetAuthModelIdentifier() (string, uint) {
	return "bnv_ldap", u.ID
}

func (u *User) UpdateLastLogin(echo.Context, *gorm.DB, time.Time) {

}

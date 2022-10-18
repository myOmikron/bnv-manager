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
	Username    string
	IsClubAdmin bool `gorm:"not null"`
	IsAdmin     bool `gorm:"not null"`
	LastLogin   *time.Time
}

func (u *User) GetAuthModelIdentifier() (string, uint) {
	return "bnv_ldap", u.ID
}

func (u *User) UpdateLastLogin(c echo.Context, db *gorm.DB, login time.Time) {
	u.LastLogin = &login
	if err := db.Save(&u).Error; err != nil {
		c.Logger().Error(err)
	}
}

package ldap_impl

import (
	"context"
	"errors"
	"fmt"

	l "github.com/go-ldap/ldap/v3"
	"github.com/myOmikron/echotools/worker"
	"gorm.io/gorm"
	"gorm.io/gorm/utils"

	"github.com/myOmikron/bnv-manager/models/config"
	"github.com/myOmikron/bnv-manager/models/dbmodels"
)

func Authenticate(username string, password string, db *gorm.DB, config *config.Config, roWP worker.Pool) (*dbmodels.User, error) {
	var userDN string
	var memberOf []string

	t := worker.NewTaskWithContext(func(ctx context.Context) error {
		conn := ctx.Value("conn").(*l.Conn)

		// Search for the given username
		sr, err := conn.Search(
			l.NewSearchRequest(
				config.LDAP.UserSearchBase,
				l.ScopeSingleLevel, l.NeverDerefAliases, 0, 0, false,
				fmt.Sprintf(config.LDAP.UserSearchFilter, l.EscapeFilter(username)),
				[]string{"dn", "memberOf"},
				nil,
			),
		)
		if err != nil {
			return err
		}

		if len(sr.Entries) != 1 {
			return errors.New("user does not exist or too many entries returned")
		}

		userDN = sr.Entries[0].DN
		memberOf = sr.Entries[0].GetAttributeValues("memberOf")

		// Bind as the user to verify their password
		if err := conn.Bind(userDN, password); err != nil {
			return err
		}

		// Rebind as ro user
		if err := conn.Bind(config.LDAP.ROBindUser, config.LDAP.ROBindPassword); err != nil {
			return err
		}

		return nil
	})

	roWP.AddTask(t)

	if err := t.WaitForResult(); err != nil {
		return nil, err
	}

	var u dbmodels.User
	var count int64
	db.Find(&u, "dn = ?", userDN).Count(&count)
	if count == 0 {
		u.DN = userDN
		u.IsAdmin = utils.Contains(memberOf, config.LDAP.AdminGroupDN)
		u.IsClubAdmin = utils.Contains(memberOf, config.LDAP.ClubAdminGroupDN)
		u.Username = username
		db.Create(&u)
	} else {
		u.IsAdmin = utils.Contains(memberOf, config.LDAP.AdminGroupDN)
		u.IsClubAdmin = utils.Contains(memberOf, config.LDAP.ClubAdminGroupDN)
		db.Save(&u)
	}

	return &u, nil
}

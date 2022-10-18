package ldap_impl

import (
	"crypto/tls"
	"errors"
	"fmt"
	"gorm.io/gorm/utils"

	l "github.com/go-ldap/ldap/v3"
	"gorm.io/gorm"

	"github.com/myOmikron/bnv-manager/models/config"
	"github.com/myOmikron/bnv-manager/models/dbmodels"
)

func Authenticate(username string, password string, db *gorm.DB, config *config.Config) (*dbmodels.User, error) {
	var u dbmodels.User

	tlsConfig := l.DialWithTLSConfig(&tls.Config{InsecureSkipVerify: true})
	conn, err := l.DialURL(config.LDAP.ServerURI, tlsConfig)
	if err != nil {
		return nil, err
	}
	defer conn.Close()

	// First bind with a read only user
	err = conn.Bind(config.LDAP.ROBindUser, config.LDAP.ROBindPassword)
	if err != nil {
		return nil, err
	}

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
		return nil, err
	}

	if len(sr.Entries) != 1 {
		return nil, errors.New("user does not exist or too many entries returned")
	}

	userDN := sr.Entries[0].DN
	memberOf := sr.Entries[0].GetAttributeValues("memberOf")

	// Bind as the user to verify their password
	err = conn.Bind(userDN, password)
	if err != nil {
		return nil, err
	}

	var count int64
	db.Find(&u, "dn = ?", userDN).Count(&count)
	if count == 0 {
		u.DN = userDN
		u.IsAdmin = utils.Contains(memberOf, config.LDAP.AdminGroupDN)
		u.IsClubAdmin = utils.Contains(memberOf, config.LDAP.ClubAdminGroupDN)
		db.Create(&u)
	} else {
		u.IsAdmin = utils.Contains(memberOf, config.LDAP.AdminGroupDN)
		u.IsClubAdmin = utils.Contains(memberOf, config.LDAP.ClubAdminGroupDN)
		db.Save(&u)
	}

	return &u, nil
}

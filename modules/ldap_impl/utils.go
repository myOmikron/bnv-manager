package ldap_impl

import (
	"errors"
	"fmt"
	"gorm.io/gorm/utils"
	"regexp"
	"strings"

	l "github.com/go-ldap/ldap/v3"
	"golang.org/x/crypto/bcrypt"

	"github.com/myOmikron/bnv-manager/models/config"
)

func HashPassword(password string) (*string, error) {
	hashed, err := bcrypt.GenerateFromPassword([]byte(password), 12)
	if err != nil {
		return nil, err
	}
	s := string(hashed)
	return &s, nil
}

var nonAlphanumericRegex = regexp.MustCompile(`[^a-zA-Z0-9 ]+`)

func GenerateUsername(firstname string, surname string, config *config.Config) (username *string, err error) {
	if len(firstname) == 0 && len(surname) == 0 {
		return nil, errors.New("firstname and surname must not be both empty")
	}

	mapping := []struct {
		old string
		new string
	}{{"ö", "oe"}, {"ü", "ue"}, {"ä", "ae"}, {"ß", "ss"}}
	for _, m := range mapping {
		firstname = strings.ReplaceAll(firstname, m.old, m.new)
		surname = strings.ReplaceAll(surname, m.old, m.new)
	}
	firstname = strings.ToLower(nonAlphanumericRegex.ReplaceAllString(firstname, ""))
	surname = strings.ToLower(nonAlphanumericRegex.ReplaceAllString(surname, ""))

	if len(surname) == 0 {
		username = &firstname
	} else if len(firstname) == 0 {
		username = &surname
	} else {
		u := fmt.Sprintf("%s.%s", firstname, surname)
		username = &u
	}

	conn, err := l.DialURL(config.LDAP.ServerURI)
	if err != nil {
		return nil, err
	}
	defer conn.Close()
	if err := conn.Bind(config.LDAP.ROBindUser, config.LDAP.ROBindPassword); err != nil {
		return nil, err
	}
	defer conn.Unbind()

	sr, err := conn.Search(l.NewSearchRequest(
		config.LDAP.UserSearchBase,
		l.ScopeSingleLevel, l.NeverDerefAliases, 0, 0, false,
		fmt.Sprintf("(cn=%s*)", l.EscapeFilter(*username)),
		[]string{"cn"},
		nil,
	))
	if err != nil {
		return nil, err
	}

	cns := make([]string, 0)
	for _, entry := range sr.Entries {
		cns = append(cns, entry.GetAttributeValue("cn"))
	}

	counter := 1
	orig := *username
	for {
		if !utils.Contains(cns, *username) {
			break
		}
		u := fmt.Sprintf("%s%d", orig, counter)
		username = &u
		counter++
	}

	return
}

func AddDNToGroup(dn string, groupDN string, config *config.Config) error {
	conn, err := l.DialURL(config.LDAP.ServerURI)
	if err != nil {
		return err
	}
	defer conn.Close()

	if err := conn.Bind(config.LDAP.AdminBindUser, config.LDAP.AdminBindPassword); err != nil {
		return err
	}
	defer conn.Unbind()

	mod := l.NewModifyRequest(groupDN, []l.Control{})
	mod.Add("member", []string{dn})
	if err := conn.Modify(mod); err != nil {
		return err
	}

	return nil
}

func CreateUser(
	username string,
	firstname string,
	surname string,
	password string,
	mail *string,
	config *config.Config,
) (*string, error) {
	hashed, err := HashPassword(password)
	if err != nil {
		return nil, err
	}
	dn := fmt.Sprintf("cn=%s,%s", username, config.LDAP.UserSearchBase)

	conn, err := l.DialURL(config.LDAP.ServerURI)
	if err != nil {
		return nil, err
	}
	defer conn.Close()

	if err := conn.Bind(config.LDAP.AdminBindUser, config.LDAP.AdminBindPassword); err != nil {
		return nil, err
	}
	defer conn.Unbind()

	attrs := []l.Attribute{
		{"objectClass", []string{"top", "inetOrgPerson"}},
		{"cn", []string{username}},
		{"givenName", []string{firstname}},
		{"sn", []string{surname}},
		{"userPassword", []string{*hashed}},
	}

	if mail != nil {
		attrs = append(attrs, l.Attribute{Type: "mail", Vals: []string{*mail}})
	}

	if err := conn.Add(&l.AddRequest{
		DN:         dn,
		Attributes: attrs,
		Controls:   nil,
	}); err != nil {
		return nil, err
	}

	return &dn, nil
}

type Club struct {
	DN string
	CN string
}

func GetAllClubs(config *config.Config) ([]Club, error) {
	conn, err := l.DialURL(config.LDAP.ServerURI)
	if err != nil {
		return nil, err
	}
	defer conn.Close()

	if err := conn.Bind(config.LDAP.ROBindUser, config.LDAP.ROBindPassword); err != nil {
		return nil, err
	}
	defer conn.Unbind()

	sr, err := conn.Search(l.NewSearchRequest(
		config.LDAP.ClubSearchBase,
		l.ScopeSingleLevel, l.NeverDerefAliases, 0, 0, false,
		fmt.Sprintf(config.LDAP.ClubSearchFilter, "*"),
		[]string{"dn", "cn"},
		nil,
	))
	if err != nil {
		return nil, err
	}

	groupDNs := make([]Club, 0)
	for _, entry := range sr.Entries {
		groupDNs = append(groupDNs, Club{
			DN: entry.GetAttributeValue("dn"),
			CN: entry.GetAttributeValue("cn"),
		})
	}

	return groupDNs, nil
}

func CheckIfClubExists(name string, config *config.Config) (*string, error) {
	conn, err := l.DialURL(config.LDAP.ServerURI)
	if err != nil {
		return nil, err
	}
	defer conn.Close()

	if err := conn.Bind(config.LDAP.ROBindUser, config.LDAP.ROBindPassword); err != nil {
		return nil, err
	}
	defer conn.Unbind()

	sr, err := conn.Search(l.NewSearchRequest(
		config.LDAP.ClubSearchBase,
		l.ScopeSingleLevel, l.NeverDerefAliases, 0, 0, false,
		fmt.Sprintf(config.LDAP.ClubSearchFilter, l.EscapeFilter(name)),
		nil,
		nil,
	))
	if err != nil {
		return nil, err
	}

	if len(sr.Entries) == 1 {
		return &sr.Entries[0].DN, nil
	}
	return nil, nil
}

type User struct {
	DN        string
	CN        string
	Firstname string
	Surname   string
	Mail      *string
}

func GetClubadmins(club string, config *config.Config) ([]User, error) {
	conn, err := l.DialURL(config.LDAP.ServerURI)
	if err != nil {
		return nil, err
	}
	defer conn.Close()

	if err := conn.Bind(config.LDAP.ROBindUser, config.LDAP.ROBindPassword); err != nil {
		return nil, err
	}
	defer conn.Unbind()

	sr, err := conn.Search(l.NewSearchRequest(
		config.LDAP.UserSearchBase,
		l.ScopeSingleLevel, l.NeverDerefAliases, 0, 0, false,
		fmt.Sprintf(
			"(&(objectClass=inetOrgPerson)(memberOf=cn=%s,%s)(memberOf=%s))",
			l.EscapeFilter(club),
			config.LDAP.ClubSearchBase,
			config.LDAP.ClubAdminGroupDN,
		),
		[]string{"dn", "cn", "sn", "givenName"},
		nil,
	))
	if err != nil {
		return nil, err
	}

	results := make([]User, 0)

	for _, entry := range sr.Entries {
		results = append(results, User{
			DN:        entry.DN,
			CN:        entry.GetAttributeValue("cn"),
			Firstname: entry.GetAttributeValue("givenName"),
			Surname:   entry.GetAttributeValue("sn"),
			Mail:      nil,
		})
	}

	return results, nil
}

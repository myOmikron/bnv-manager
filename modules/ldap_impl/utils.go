package ldap_impl

import (
	"context"
	"errors"
	"fmt"
	"regexp"
	"strings"

	l "github.com/go-ldap/ldap/v3"
	"github.com/myOmikron/echotools/worker"
	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm/utils"

	"github.com/myOmikron/bnv-manager/models/config"
)

func HashPassword(password string) (*string, error) {
	hashed, err := bcrypt.GenerateFromPassword([]byte(password), 12)
	if err != nil {
		return nil, err
	}
	s := fmt.Sprintf("{CRYPT}%s", string(hashed))
	return &s, nil
}

var nonAlphanumericRegex = regexp.MustCompile(`[^a-zA-Z0-9]+`)

func GenerateUsername(firstname string, surname string, config *config.Config, roWP worker.Pool) (username *string, err error) {
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

	cns := make([]string, 0)

	t := worker.NewTaskWithContext(func(ctx context.Context) error {
		conn := ctx.Value("conn").(*l.Conn)

		sr, err := conn.Search(l.NewSearchRequest(
			config.LDAP.UserSearchBase,
			l.ScopeSingleLevel, l.NeverDerefAliases, 0, 0, false,
			fmt.Sprintf("(cn=%s*)", l.EscapeFilter(*username)),
			[]string{"cn"},
			nil,
		))
		if err != nil {
			return err
		}

		for _, entry := range sr.Entries {
			cns = append(cns, entry.GetAttributeValue("cn"))
		}

		return nil
	})

	roWP.AddTask(t)

	if err := t.WaitForResult(); err != nil {
		return nil, err
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

func AddDNToGroup(dn string, groupDN string, adminPool worker.Pool) error {
	t := worker.NewTaskWithContext(func(ctx context.Context) error {
		conn := ctx.Value("conn").(*l.Conn)

		mod := l.NewModifyRequest(groupDN, []l.Control{})
		mod.Add("member", []string{dn})
		if err := conn.Modify(mod); err != nil {
			return err
		}

		return nil
	})

	adminPool.AddTask(t)

	if err := t.WaitForResult(); err != nil {
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
	adminWP worker.Pool,
) (*string, error) {
	hashed, err := HashPassword(password)
	if err != nil {
		return nil, err
	}
	dn := fmt.Sprintf("cn=%s,%s", username, config.LDAP.UserSearchBase)

	t := worker.NewTaskWithContext(func(ctx context.Context) error {
		conn := ctx.Value("conn").(*l.Conn)

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

		if err := conn.Add(&l.AddRequest{DN: dn, Attributes: attrs, Controls: nil}); err != nil {
			return err
		}

		return nil
	})

	adminWP.AddTask(t)

	if err := t.WaitForResult(); err != nil {
		return nil, err
	}

	return &dn, nil
}

type Club struct {
	DN          string
	CN          string
	Description string
}

func GetAllClubs(config *config.Config, roWP worker.Pool) ([]Club, error) {
	groupDNs := make([]Club, 0)

	t := worker.NewTaskWithContext(func(ctx context.Context) error {
		conn := ctx.Value("conn").(*l.Conn)

		sr, err := conn.Search(l.NewSearchRequest(
			config.LDAP.ClubSearchBase,
			l.ScopeSingleLevel, l.NeverDerefAliases, 0, 0, false,
			fmt.Sprintf(config.LDAP.ClubSearchFilter, "*"),
			[]string{"dn", "cn", "description"},
			nil,
		))
		if err != nil {
			return err
		}

		for _, entry := range sr.Entries {
			groupDNs = append(groupDNs, Club{
				DN:          entry.GetAttributeValue("dn"),
				CN:          entry.GetAttributeValue("cn"),
				Description: entry.GetAttributeValue("description"),
			})
		}

		return nil
	})

	roWP.AddTask(t)

	if err := t.WaitForResult(); err != nil {
		return nil, err
	}

	return groupDNs, nil
}

func CheckIfClubExists(name string, config *config.Config, roWP worker.Pool) (*string, error) {
	var ret *string

	t := worker.NewTaskWithContext(func(ctx context.Context) error {
		conn := ctx.Value("conn").(*l.Conn)

		sr, err := conn.Search(l.NewSearchRequest(
			config.LDAP.ClubSearchBase,
			l.ScopeSingleLevel, l.NeverDerefAliases, 0, 0, false,
			fmt.Sprintf(config.LDAP.ClubSearchFilter, l.EscapeFilter(name)),
			nil,
			nil,
		))
		if err != nil {
			return err
		}

		if len(sr.Entries) == 1 {
			ret = &sr.Entries[0].DN
		}

		return nil
	})

	roWP.AddTask(t)

	if err := t.WaitForResult(); err != nil {
		return nil, err
	}

	return ret, nil
}

type User struct {
	DN        string
	CN        string
	Firstname string
	Surname   string
	Mail      *string
}

func GetClubadmins(club string, config *config.Config, roWP worker.Pool) ([]User, error) {
	results := make([]User, 0)

	t := worker.NewTaskWithContext(func(ctx context.Context) error {
		conn := ctx.Value("conn").(*l.Conn)

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
			return err
		}

		for _, entry := range sr.Entries {
			results = append(results, User{
				DN:        entry.DN,
				CN:        entry.GetAttributeValue("cn"),
				Firstname: entry.GetAttributeValue("givenName"),
				Surname:   entry.GetAttributeValue("sn"),
				Mail:      nil,
			})
		}

		return nil
	})

	roWP.AddTask(t)

	if err := t.WaitForResult(); err != nil {
		return nil, err
	}

	return results, nil
}

func CreateClub(id string, name string, config *config.Config, adminWP worker.Pool) error {
	t := worker.NewTaskWithContext(func(ctx context.Context) error {
		conn := ctx.Value("conn").(*l.Conn)

		addRequest := l.NewAddRequest(fmt.Sprintf("cn=%s,%s", l.EscapeFilter(id), config.LDAP.ClubSearchBase), nil)
		addRequest.Attribute("objectClass", []string{"top", "groupOfNames"})
		addRequest.Attribute("description", []string{name})
		addRequest.Attribute("member", []string{config.LDAP.DummyUserDN})

		if err := conn.Add(addRequest); err != nil {
			return err
		}

		return nil
	})

	adminWP.AddTask(t)

	if err := t.WaitForResult(); err != nil {
		return err
	}

	return nil
}

func DeleteClub(id string, config *config.Config, adminWP worker.Pool) error {
	clubDN := fmt.Sprintf("cn=%s,%s", l.EscapeFilter(id), config.LDAP.ClubSearchBase)

	t := worker.NewTaskWithContext(func(ctx context.Context) error {
		conn := ctx.Value("conn").(*l.Conn)

		sr, err := conn.Search(
			l.NewSearchRequest(
				config.LDAP.UserSearchBase,
				l.ScopeSingleLevel,
				l.NeverDerefAliases, 0, 0, false,
				fmt.Sprintf("(&(objectClass=inetOrgPerson)(memberOf=%s))", clubDN),
				[]string{"dn"},
				nil,
			),
		)
		if err != nil {
			return err
		}

		if err := conn.Del(l.NewDelRequest(clubDN, nil)); err != nil {
			return err
		}

		for _, entry := range sr.Entries {
			if err := conn.Del(l.NewDelRequest(entry.DN, nil)); err != nil {
				return err
			}
		}

		return nil
	})

	adminWP.AddTask(t)

	if err := t.WaitForResult(); err != nil {
		return err
	}

	return nil
}

func ChangePasswordForDN(dn string, password string, adminWP worker.Pool) error {
	hashed, err := HashPassword(password)
	if err != nil {
		return err
	}

	t := worker.NewTaskWithContext(func(ctx context.Context) error {
		conn := ctx.Value("conn").(*l.Conn)

		modReq := l.NewModifyRequest(dn, nil)
		modReq.Replace("userPassword", []string{*hashed})

		if err := conn.Modify(modReq); err != nil {
			return err
		}

		return nil
	})

	adminWP.AddTask(t)

	if err := t.WaitForResult(); err != nil {
		return err
	}

	return nil
}

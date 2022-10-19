package config

import (
	"errors"
	"fmt"
	"net/url"
	"strings"

	"github.com/myOmikron/echotools/color"
	"gorm.io/gorm/utils"
)

var allowedDrivers = []string{"sqlite", "mysql", "postgresql"}

type Error struct {
	Section   string
	Parameter string
	Err       error
}

func (c *Error) Error() string {
	return fmt.Sprintf(
		"%s\n\n%s\n%s: %s\n",
		color.Colorize(color.RED, "Configuration failure:"),
		color.Colorize(color.BLUE, c.Section),
		c.Parameter,
		c.Err.Error(),
	)
}

type Server struct {
	ListenAddress           string
	ListenPort              uint16
	PublicURI               string
	AllowedHosts            []string
	UseForwardedProtoHeader bool
}

type Database struct {
	Driver   string
	Name     string
	Host     string
	Port     uint16
	User     string
	Password string
}

type LDAP struct {
	ServerURI         string
	AdminBindUser     string
	AdminBindPassword string
	ROBindUser        string
	ROBindPassword    string
	UserSearchBase    string
	UserSearchFilter  string
	ClubSearchBase    string
	ClubSearchFilter  string
	ClubAdminGroupDN  string
	AdminGroupDN      string
}

type Config struct {
	Server   Server
	Database Database
	LDAP     LDAP
}

func (conf *Config) CheckConfig() error {
	if conf.Server.ListenPort < 1 || conf.Server.ListenPort > 1<<15-1 {
		return &Error{
			Err:       errors.New("invalid app port"),
			Section:   "[Server]",
			Parameter: "ListenPort",
		}
	}

	if !strings.HasPrefix(conf.Server.PublicURI, "https://") &&
		!strings.HasPrefix(conf.Server.PublicURI, "http://") {
		return &Error{
			Err:       errors.New("invalid public uri prefix. Only https:// or http:// are valid prefixes"),
			Section:   "[Server]",
			Parameter: "PublicURI",
		}
	}

	if _, err := url.Parse(conf.Server.PublicURI); err != nil {
		return &Error{
			Err:       errors.New("invalid public uri"),
			Section:   "[Server]",
			Parameter: "PublicURI",
		}
	}

	if len(conf.Server.AllowedHosts) == 0 {
		return &Error{
			Err:       errors.New("empty value is forbidden, as the server will not respond to anything"),
			Section:   "[Server]",
			Parameter: "AllowedHosts",
		}
	}
	for _, allowedHost := range conf.Server.AllowedHosts {
		if !strings.HasPrefix(allowedHost, "https://") && !strings.HasPrefix(allowedHost, "http://") {
			return &Error{
				Err:       errors.New("must be starting with either http:// or https://"),
				Section:   "[Section]",
				Parameter: "AllowedHosts",
			}
		}
		if _, err := url.Parse(allowedHost); err != nil {
			return &Error{
				Err:       err,
				Section:   "[Section]",
				Parameter: "AllowedHosts",
			}
		}
	}

	l := strings.ToLower(conf.Database.Driver)
	if !utils.Contains(allowedDrivers, l) {
		return &Error{
			Err:       errors.New(fmt.Sprintf("driver must be in %s", strings.Join(allowedDrivers, ", "))),
			Section:   "[Database]",
			Parameter: "Driver",
		}
	}
	conf.Database.Driver = l

	if conf.Database.Name == "" {
		return &Error{
			Err:       errors.New("name must not be empty"),
			Section:   "[Database]",
			Parameter: "Name",
		}
	}

	switch conf.Database.Driver {
	case "mysql", "postgresql":
		if conf.Database.Port <= 0 || conf.Database.Port > 1<<15-1 {
			return &Error{Err: errors.New("not a valid port"), Section: "[Database]", Parameter: "Port"}
		}
		if conf.Database.Host == "" {
			return &Error{Err: errors.New("invalid host"), Section: "[Database]", Parameter: "Host"}
		}
		if conf.Database.User == "" {
			return &Error{Err: errors.New("must not be empty"), Section: "[Database]", Parameter: "User"}
		}
		if conf.Database.Password == "" {
			return &Error{Err: errors.New("must not be empty"), Section: "[Database]", Parameter: "Password"}
		}
	}

	return nil
}

func (conf *Config) GetListenString() string {
	return conf.Server.ListenAddress + ":" + fmt.Sprint(conf.Server.ListenPort)
}

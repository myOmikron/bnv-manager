package handler

import (
	"errors"
	"regexp"

	"github.com/myOmikron/echotools/worker"
	"gorm.io/gorm"

	"github.com/myOmikron/bnv-manager/models/config"
)

type Wrapper struct {
	DB         *gorm.DB
	Config     *config.Config
	ReadOnlyWP worker.Pool
	AdminWP    worker.Pool
}

var (
	lowerCaseAscii = regexp.MustCompile("[a-z]")
	upperCaseAscii = regexp.MustCompile("[A-Z]")
)

func (w *Wrapper) checkPassword(password string) error {
	var hasUpper, hasLower, hasSpecial bool
	for _, r := range []rune(password) {
		if lowerCaseAscii.MatchString(string(r)) {
			hasLower = true
		} else if upperCaseAscii.MatchString(string(r)) {
			hasUpper = true
		} else {
			hasSpecial = true
		}

		if hasLower && hasUpper && hasSpecial {
			break
		}
	}
	if len(password) < 12 {
		return errors.New("password must have a minimum 12 characters")
	} else if !hasLower || !hasUpper {
		return errors.New("password must have lower and upper case characters")
	} else if !hasSpecial {
		return errors.New("password must have at least one special character")
	}

	return nil
}

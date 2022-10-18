package handler

import (
	"gorm.io/gorm"

	"github.com/myOmikron/bnv-manager/models/config"
)

type Wrapper struct {
	DB     *gorm.DB
	Config *config.Config
}

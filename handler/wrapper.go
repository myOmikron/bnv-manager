package handler

import (
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

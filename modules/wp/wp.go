package wp

import (
	"context"

	l "github.com/go-ldap/ldap/v3"
	"github.com/myOmikron/echotools/worker"

	"github.com/myOmikron/bnv-manager/models/config"
)

type w struct {
	Conn  *l.Conn
	queue chan worker.Task
	quit  chan bool
}

func (w *w) SetQueue(c chan worker.Task) {
	w.queue = c
}

func (w *w) Start() {
	ctx := context.WithValue(context.Background(), "conn", w.Conn)
	for {
		select {
		case <-w.quit:
			return
		case t := <-w.queue:
			t.ExecuteWithContext(ctx)
		}
	}
}

func (w *w) Stop() {
	go func() {
		w.quit <- true
	}()
}

func StartAdminWorker(config *config.Config) func() (worker.Worker, error) {
	return func() (worker.Worker, error) {
		conn, err := l.DialURL(config.LDAP.ServerURI)
		if err != nil {
			return nil, err
		}

		if err := conn.Bind(config.LDAP.AdminBindUser, config.LDAP.AdminBindPassword); err != nil {
			return nil, err
		}

		return &w{
			Conn: conn,
			quit: make(chan bool),
		}, nil
	}
}

func StartROWorker(config *config.Config) func() (worker.Worker, error) {
	return func() (worker.Worker, error) {
		conn, err := l.DialURL(config.LDAP.ServerURI)
		if err != nil {
			return nil, err
		}

		if err := conn.Bind(config.LDAP.ROBindUser, config.LDAP.ROBindPassword); err != nil {
			return nil, err
		}

		return &w{
			Conn: conn,
			quit: make(chan bool),
		}, nil
	}
}

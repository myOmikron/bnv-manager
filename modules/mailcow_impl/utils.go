package mailcow_impl

import (
	"context"
	"go.bnck.me/mailcow"

	"github.com/myOmikron/bnv-manager/models/config"
)

func GetDomains(config *config.Config) ([]string, error) {
	client, err := mailcow.New(config.Mailcow.ServerURI, config.Mailcow.APIKey)
	if err != nil {
		return nil, err
	}

	domainClient := client.Domain()
	all, err := domainClient.All(context.Background())
	if err != nil {
		return nil, err
	}

	domains := make([]string, 0)
	for _, d := range all {
		if d.Active == 1 {
			domains = append(domains, d.DomainName)
		}
	}

	return domains, nil
}

package models

type JsonConf struct {
	Server struct {
		Path    string `json:"path"`
		Address string `json:"address"`
		Https   bool   `json:"https"`
	} `json:"server"`
	Vault struct {
		Url   string `json:"url"`
		Token string `json:"token"`
	} `json:"vault"`
	Mail struct {
		Host string `json:"host"`
		Port string `json:"port"`
	} `json:"mail"`
	Jenkins struct {
		Url string `json:"url"`
	} `json:"jenkins"`
	Status struct {
		Url string `json:"url"`
	} `json:"status"`
        Jfrog struct {
                Url string `json:"url"`
        } `json:"jfrog"`
}

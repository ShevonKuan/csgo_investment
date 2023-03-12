package main

import (
	"database/sql"
	"fmt"
	"io"
	"net/http"
	"strings"

	_ "github.com/mattn/go-sqlite3"

	"github.com/tidwall/gjson"
)

var (
	schemaSQL string = `CREATE TABLE IF NOT EXISTS youpinItem (
		Id  VARCHAR(32) PRIMARY KEY,
		CommodityName  VARCHAR(32),
		CommodityHashName  VARCHAR(32),
		IconUrlLarge  VARCHAR(32)
	);`
	insertSQL string = `INSERT OR IGNORE INTO youpinItem (
		Id, CommodityName, CommodityHashName, IconUrlLarge
		) VALUES (?, ?, ?, ?);`
)

type youpinItem struct {
	Id                string
	CommodityName     string
	CommodityHashName string
	IconUrlLarge      string
}

type youpinDB struct {
	sql  *sql.DB
	stmt *sql.Stmt
	tx   *sql.Tx
}

func (d *youpinDB) init() { // init database
	database, err := sql.Open("sqlite3", "./youpinDB.db")
	d.sql = database
	if err != nil {
		fmt.Println(err)
		return
	}
	_, err = d.sql.Exec(schemaSQL)
	if err != nil {
		fmt.Println(err)
		return
	}
	d.stmt, err = d.sql.Prepare(insertSQL)
	if err != nil {
		fmt.Println(err)
		return
	}
	tx, err := d.sql.Begin()
	if err != nil {
		fmt.Println(err)
		return
	}
	d.tx = tx

}
func (d *youpinDB) add(i *youpinItem) {

	_, err := d.tx.Stmt(d.stmt).Exec(i.Id, i.CommodityName, i.CommodityHashName, i.IconUrlLarge)
	if err != nil {
		fmt.Println(err)
		d.tx.Rollback()
		return

	}
}
func (d *youpinDB) commit() {
	err := d.tx.Commit()
	if err != nil {
		fmt.Println(err)
		return
	}
}
func (d *youpinDB) close() {

	d.stmt.Close()
	d.sql.Close()
}
func youpinCrawler(pageIndex int) *[]youpinItem {

	url := "https://api.youpin898.com/api/homepage/es/template/GetCsGoPagedList"
	method := "POST"
	reqData := fmt.Sprintf(`{
    "listType": "10",
    "gameId": "730",
    "pageIndex": "%d",
    "pageSize": 40,
    "sortType": "0",
    "listSortType": "2",
    "stickersIsSort": false
}`, pageIndex)

	payload := strings.NewReader(reqData)

	client := &http.Client{}
	req, err := http.NewRequest(method, url, payload)

	if err != nil {
		fmt.Println(err)
		return nil
	}
	req.Header.Add("authority", "api.youpin898.com")
	req.Header.Add("accept", "application/json, text/plain, */*")
	req.Header.Add("accept-language", "zh-HK,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,yue-CN;q=0.5,yue-HK;q=0.4,yue;q=0.3")
	req.Header.Add("apptype", "1")
	req.Header.Add("authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJjYTZlZTBiYzY4MzI0NTQzODI0NDkzODUyNjhiNjNhMCIsIm5hbWVpZCI6IjE2NTA4NjAiLCJJZCI6IjE2NTA4NjAiLCJ1bmlxdWVfbmFtZSI6InNoZXZvbiIsIk5hbWUiOiJzaGV2b24iLCJuYmYiOjE2Nzg1NDYwNTksImV4cCI6MTY3OTQxMDA1OSwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.oTdRw25vO9Z5lPPhvJK6s9fGGUdVdj-Rv7aan4JrhZ8")
	req.Header.Add("cache-control", "no-cache")
	req.Header.Add("content-type", "application/json")
	req.Header.Add("dnt", "1")
	req.Header.Add("origin", "https://youpin898.com")
	req.Header.Add("pragma", "no-cache")
	req.Header.Add("referer", "https://youpin898.com/")
	req.Header.Add("sec-ch-ua", "\"Chromium\";v=\"110\", \"Not A(Brand\";v=\"24\", \"Google Chrome\";v=\"110\"")
	req.Header.Add("sec-ch-ua-mobile", "?0")
	req.Header.Add("sec-ch-ua-platform", "\"Windows\"")
	req.Header.Add("sec-fetch-dest", "empty")
	req.Header.Add("sec-fetch-mode", "cors")
	req.Header.Add("sec-fetch-site", "same-site")
	req.Header.Add("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

	resp, err := client.Do(req)
	if err != nil {
		fmt.Println(err)
		return nil
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		fmt.Println(err)
		return nil
	}
	// json
	res := gjson.ParseBytes(body)
	fmt.Println(res)
	output := []youpinItem{}
	for _, data := range res.Get("Data").Array() {
		//fmt.Println(data.Get("CommodityName").String())
		output = append(output, youpinItem{data.Get("Id").String(), data.Get("CommodityName").String(), data.Get("CommodityHashName").String(), data.Get("IconUrlLarge").String()})
	}
	return &output
}

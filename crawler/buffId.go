package main

import (
	"database/sql"
	"fmt"
	"io"
	"net/http"

	_ "github.com/mattn/go-sqlite3"

	"github.com/tidwall/gjson"
)

type buffItem struct {
	Id                string
	CommodityName     string
	CommodityHashName string
}

type buffDB struct {
	sql  *sql.DB
	stmt *sql.Stmt
	tx   *sql.Tx
}

func (d *buffDB) init() { // init database
	database, err := sql.Open("sqlite3", "./buffDB.db")
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
func (d *buffDB) add(i *buffItem) {

	_, err := d.tx.Stmt(d.stmt).Exec(i.Id, i.CommodityName, i.CommodityHashName, "")
	if err != nil {
		fmt.Println(err)
		d.tx.Rollback()
		return

	}
}
func (d *buffDB) commit() {
	err := d.tx.Commit()
	if err != nil {
		fmt.Println(err)
		return
	}
}
func (d *buffDB) close() {

	d.stmt.Close()
	d.sql.Close()
}
func buffCrawler(pageIndex int) *[]buffItem {

	url := "https://buff.163.com/api/market/goods?game=csgo&page_num=" + fmt.Sprint(pageIndex) + "&use_suggestion=0&_=1678546480042"
	method := "GET"

	client := &http.Client{}
	req, err := http.NewRequest(method, url, nil)

	if err != nil {
		fmt.Println(err)
		return nil
	}
	req.Header.Add("authority", "buff.163.com")
	req.Header.Add("accept", "application/json, text/javascript, */*; q=0.01")
	req.Header.Add("accept-language", "zh-HK,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,yue-CN;q=0.5,yue-HK;q=0.4,yue;q=0.3")
	req.Header.Add("cache-control", "no-cache")
	// req.Header login status cookies
	req.Header.Add("dnt", "1")
	req.Header.Add("pragma", "no-cache")
	req.Header.Add("referer", "https://buff.163.com/market/csgo")
	req.Header.Add("sec-ch-ua", "\"Chromium\";v=\"110\", \"Not A(Brand\";v=\"24\", \"Google Chrome\";v=\"110\"")
	req.Header.Add("sec-ch-ua-mobile", "?0")
	req.Header.Add("sec-ch-ua-platform", "\"Windows\"")
	req.Header.Add("sec-fetch-dest", "empty")
	req.Header.Add("sec-fetch-mode", "cors")
	req.Header.Add("sec-fetch-site", "same-origin")
	req.Header.Add("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
	req.Header.Add("x-requested-with", "XMLHttpRequest")

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
	output := []buffItem{}
	for _, data := range res.Get("data.items").Array() {
		//fmt.Println(data.Get("name").String())
		output = append(output, buffItem{data.Get("id").String(), data.Get("name").String(), data.Get("market_hash_name").String()})
	}
	return &output
}

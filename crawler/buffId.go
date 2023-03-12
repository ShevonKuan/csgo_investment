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
	req.Header.Add("cookie", "mail_psc_fingerprint=5785c624d840bdb738bcb66d0e1e7069; nts_mail_user=18038806477@163.com:-1:1; _ntes_nuid=22df2aef1d8b0e1f6ffa202c95ebaf07; _ntes_nnid=22df2aef1d8b0e1f6ffa202c95ebaf07,1673237807890; __bid_n=1864dd2b312e2967864207; FPTOKEN=F3bVr1/Uslf9TsR9hESGNYs+bYI/wjlKozxtwtU9Ddo9nTrFXHCg26sX0FSv18QR4itlqXN8argTBmKnQajgSnBVCktYKqjKs7cmEIX3njPxMNvnBR8OOLeml/GkbiNJTDMnUM5xIXvIP0TQTD7aFRw1Rby54zbCbhvnkyW9v+Yb9CQrd0zL1dJS7PQ/DIW/j1SiXjwmp9/qYfi9ymG60lawjjsLCmADe7TneOoFbo85W/Kh3MA4tmAKMR28fjzvfK0wVrnxoAqKlzi+1HqTDdqDEx+/hnH4TSX8UxI4Dd4bWOeHqKRnbfnoRkxd4TFQ+dv8Ps2flEJ2E2lNY2g/ALT8eetcvVtP63m9bOOszhab21/VZXw0Rno9dr+TivJpIeC1DM6yvxQpKxzn/cdCmw==|s6EiMJ3yTGtKJdH/fTDbPSpsO3vBjNz0nRD6fpKZAFQ=|10|e86cc44e35f63b59db49d8734f87d550; Device-Id=7Bm8drMRjuAWlBYtOiig; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=03yCvjwC87ojmYdvfPR5Iu3wOphEceaf38cNtpu1icpvO1zGOBYERDVoqYU71wu2zyEVfQSClPFvhVSiuLC6ZMpaXwqnaacOK_raTIq7cVwtYhQJ_4SCGOptRceoR8hwmnosD7hZrv5lzfLrMVb41nRUqWlB56IChJowMicTU_F.bsoHByDSfNt7jQ.YD__iG3YkjpgasFHopJl5.Jf_KaQdRsv8uI__SkceRM0z7fiik; S_INFO=1678546478|0|0&60##|18038806477; P_INFO=18038806477|1678546478|1|netease_buff|00&99|gud&1678546412&netease_buff#gud&440100#10#0#0|&0|null|18038806477; remember_me=U1097847320|hKAVjr5BGcVKDYMMKpS9EykrXbvd6TDH; session=1-Z_bfFE-7bWQ6hrhh9ISJV_x-NnETqLQx0IOCqnjveU6J2040614208; csrf_token=IjkyNmRlNTRlMzgwOWU5Y2QxZjAwMDhlNGI1ZTE3YWQxZTNhZGIzZTMi.Fu4ohQ.qo6_Er5qoCTPsYe2M6wBSR8P1xA; csrf_token=IjkyNmRlNTRlMzgwOWU5Y2QxZjAwMDhlNGI1ZTE3YWQxZTNhZGIzZTMi.Fu5q_w.cKc-wkFdvNpCuX7tHkHsYObuA5g; session=1-Z_bfFE-7bWQ6hrhh9ISJV_x-NnETqLQx0IOCqnjveU6J2040614208")
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

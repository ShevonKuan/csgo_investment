package main

import (
	"fmt"
	"sync"
	"time"
)

func main() {
	wg := sync.WaitGroup{}
	wg.Add(1)
	go func() {
		defer wg.Done()

		for i := 100; i < 300; i++ {
			db := new(youpinDB)
			db.init()

			output := youpinCrawler(i)
			count := 0
			for _, v := range *output {
				db.add(&v)
				count++
			}
			fmt.Printf("youpin page %d counts %d \n", i, count)
			if count == 0 {
				i--
				time.Sleep(time.Second * 20)
			}
			db.commit()
			db.close()
			time.Sleep(time.Second * 1)
		}

	}()
	// go func() {
	// 	defer wg.Done()

	// 	for i := 1; i < 1020; i++ {
	// 		db := new(buffDB)
	// 		db.init()
	// 		count := 0
	// 		output := buffCrawler(i)
	// 		for _, v := range *output {
	// 			db.add(&v)
	// 			count++
	// 		}
	// 		fmt.Printf("buff page %d counts %d \n", i, count)
	// 		db.commit()
	// 		db.close()
	// 		time.Sleep(time.Second * 1)
	// 	}

	// }()
	wg.Wait()

}

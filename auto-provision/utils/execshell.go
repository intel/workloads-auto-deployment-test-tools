package util

import (
	"bufio"
	"context"
	"fmt"
	"io"
	"os/exec"
	"sync"
)

func CommandShell(ctx context.Context, cmd string) error {
	// c := exec.CommandContext(ctx, "cmd", "/C", cmd)
	c := exec.CommandContext(ctx, "bash", "-c", cmd) // mac linux
	stdout, err := c.StdoutPipe()
	if err != nil {
		return err
	}
	var wg sync.WaitGroup
	wg.Add(1)
	go func(wg *sync.WaitGroup) {
		defer wg.Done()
		reader := bufio.NewReader(stdout)
		for {
			select {
			// check ctx.Done() and stop
			case <-ctx.Done():
				if ctx.Err() != nil {
					fmt.Printf("program error: %q", ctx.Err())
				} else {
					fmt.Println("program is terminated")
				}
				return
			default:
				readString, err := reader.ReadString('\n')
				if err != nil || err == io.EOF {
					return
				}
				fmt.Print(readString)
			}
		}
	}(&wg)
	err = c.Start()
	wg.Wait()
	return err
}

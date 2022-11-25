package middleware

import (
	"fmt"
	"log"
	"time"

	"github.com/gin-gonic/gin"
)

func Logger() gin.HandlerFunc {
	return func(c *gin.Context) {
		t := time.Now()
		// Set example variable
		// c.Set("logtime", "2022/03/25")
		// before request
		c.Next()
		// after requewt
		latency := time.Since(t)
		log.Print(latency)
		// access the status we are sending
		status := c.Writer.Status()
		log.Println(status)
	}
}

func LoggerFormat() gin.HandlerFunc {
	loggerContent := func(param gin.LogFormatterParams) string {
		fmt.Println(fmt.Println(param.ClientIP))
		return fmt.Sprintf(
			"%s - [%s] \"%s %s %s %d %s \"%s\" %s\"\" %s\"\n",
			param.ClientIP,
			param.TimeStamp.Format(time.RFC1123),
			param.Method,
			param.Path,
			param.Request.Proto,
			param.StatusCode,
			param.Latency,
			param.Request.UserAgent(),
			param.ErrorMessage,
			param.Request.Body,
		)
	}
	return gin.LoggerWithFormatter(loggerContent)
}

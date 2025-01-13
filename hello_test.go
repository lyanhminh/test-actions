package main

import (
	"fmt"
	"testing"
)

func TestStuff(t *testing.T) {
	fmt.Println("passing")
	//t.Errorf("testing fail")
}

func TestMoreStuff(t *testing.T) {
	fmt.Println("passing 2")
	//t.Errorf("testing fail")
}

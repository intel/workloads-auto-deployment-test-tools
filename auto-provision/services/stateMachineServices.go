package services

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/ryanfaerman/fsm"
)

type Thing struct {
	State fsm.State

	// our machine cache
	machine *fsm.Machine
}

// CurrentState Add methods to comply with the fsm.Stater interface
func (t *Thing) CurrentState() fsm.State { return t.State }
func (t *Thing) SetState(s fsm.State)    { t.State = s }

// Apply A helpful function that lets us apply arbitrary rulesets to this
// instances state machine without reallocating the machine. While not
// required, it's something I like to have.
func (t *Thing) Apply(r *fsm.Ruleset) *fsm.Machine {
	if t.machine == nil {
		t.machine = &fsm.Machine{Subject: t}
	}

	t.machine.Rules = r
	return t.machine
}

func StatusProgress(ctx *gin.Context) {
	var err error

	someThing := Thing{State: "pending"} // Our subject
	fmt.Println(someThing)

	// Establish some rules for our FSM
	rules := fsm.Ruleset{}
	rules.AddTransition(fsm.T{O: "pending", E: "%25"})
	rules.AddTransition(fsm.T{O: "pending", E: "%50"})
	rules.AddTransition(fsm.T{O: "pending", E: "%75"})
	rules.AddTransition(fsm.T{O: "pending", E: "%100"})
	// TODO set value from shell script
	err = someThing.Apply(&rules).Transition("%75")
	if err != nil {
		ctx.JSON(http.StatusOK, gin.H{
			"status": err,
		})
	} else {
		fmt.Println(someThing)
		ctx.JSON(http.StatusOK, gin.H{
			"status": someThing.State,
		})
	}
}

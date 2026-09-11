# Week 5 — Tools are an API for a fallible reader

**The question:** Would a competent stranger use your tools correctly from the
descriptions alone?

## Build

1. Audit every tool in one system: name, description, parameter schema,
   error strings, return shape.
2. From Week 3's traces, compute the **tool-error rate** per tool — wrong
   tool chosen, malformed arguments, correct call misinterpreted result.
3. Refactor the three worst:
   - Names that say what they do, in the vocabulary of the task
   - Descriptions that state when *not* to use the tool
   - Parameters that are hard to get wrong (enums over free strings, flat over
     deeply nested)
   - **Error strings that say what to do next**, not just what went wrong.
     `"No user found with id 'X'. Search by email with find_user first."`
     beats `"404"` by an enormous margin.
   - Return shapes that omit what the model won't use. Every unused field is
     context you're paying for.
4. Rerun the suite.

## Study (3h)

Anthropic's "Writing tools for agents"; Schick et al., "Toolformer"; the Model
Context Protocol specification.

## Gate

Tool-error rate per tool, before and after, on the same eval set. At least one
tool materially improved beyond the noise floor — with the number.

## Write

A tool-design convention doc for your systems. Five to eight rules you'd hold
a code review to.

## The trap

Adding more tools. When the model picks wrong, the instinct is to add a tool
for the case it missed. Usually the fix is *fewer* tools with clearer
boundaries — overlapping tools create ambiguity, and ambiguity is where
selection errors live.

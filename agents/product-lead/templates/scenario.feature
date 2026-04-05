@<epic-tag>
Feature: <Story Title>
  As a <Persona>
  I want to <action from backlog story>
  so that <benefit from backlog story>.

  Background:
    Given <shared precondition for all scenarios in this file>

  Rule: <Acceptance criterion 1 — a business rule expressed as a declarative statement>

    Scenario: <Happy path example for this rule>
      Given <concrete precondition with data>
      When <user action>
      Then <observable outcome>

    Scenario: <Edge case or alternative for this rule>
      Given <different precondition>
      When <user action>
      Then <different outcome>

  Rule: <Acceptance criterion 2>

    Scenario: <Example>
      Given <precondition>
      | column1 | column2 |
      | value1  | value2  |
      When <action>
      Then <outcome>

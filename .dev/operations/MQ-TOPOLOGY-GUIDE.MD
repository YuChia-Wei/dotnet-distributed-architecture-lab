# MQ Topology Guide

本指南定義 `.dev/operations/mq-topology.md` 的最小內容。

## 目的

讓維護者快速回答：

- 目前有哪些 broker / topic / exchange / queue
- message route 怎麼走
- retry / dead-letter / replay 策略如何配置
- 哪些 queue / topic 對哪些 bounded contexts 重要

## 最小章節

```markdown
# MQ Topology

## Scope

## Broker Inventory

## Route Map

## Retry / Dead-Letter Strategy

## Operational Risks

## Deferred Items
```

## Broker Inventory 最少欄位

- broker type
  - RabbitMQ / Kafka
- logical channel name
  - exchange / topic / queue / consumer group
- producer
- consumer
- purpose

## Route Map 最少欄位

每條 route 至少記錄：

- source event or message
- source context
- broker object
- destination consumer
- ack / retry / failure behavior summary

## Retry / Dead-Letter Strategy

至少說清楚：

- retry 是否 automatic
- max retry or retry class
- dead-letter destination
- replay responsibility
- duplicate delivery expectation

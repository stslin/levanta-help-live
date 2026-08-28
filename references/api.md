# Levanta Knowledge Base — API Documentation

Creator API and Seller API — prerequisites, authentication, webhooks, and links to the full Swagger docs at api-docs.levanta.io.

Source: <https://knowledge.levanta.io>
Snapshot date: 2026-08-23

---

## Table of contents


### Creator API

1. [Creator Webhooks](#1)
2. [More Details on the Creator API](#2)
3. [Creator API Documentation](#3)

### Seller API

4. [More Details on the Seller API](#4)
5. [Seller API Documentation](#5)

---

# Creator API

<a id="1"></a>

## 1. Creator Webhooks

**Source:** <https://knowledge.levanta.io/articles/3588852646-creator-webhooks>

# Creator Webhooks

Last updated 1 year ago

### Prerequisites

To gain access to the Levanta Webhooks, you must have a valid API key. Make sure you have followed the prerequisites as outlined in the [Creator API Documentation](https://api-docs.levanta.io/introduction)

### Introduction

Webhooks are a way to receive real-time updates from Levanta about activity happening in your account. Every time an event you are subscribed to occurs, Levanta will send your endpoint a request containing the event details. Follow the instructions below to get started!

### Getting Started

To get started with Levanta Webhooks, you can visit <https://app.levanta.io/creator/settings/api> and click “Create Endpoint”. An endpoint is a specific destination, owned by you, that is ready to receive webhook events from Levanta. Enter the URL and choose the events that you would like to subscribe to.

### Security (Recommended)

Levanta implements a Hash-based message authentication code (HMAC) to help you verify that requests are coming from Levanta’s servers. Levanta will provide a secret key, available in the webhook dashboard, that you may use for this verification process. To verify Levanta webhooks, follow the following steps for each request:

  1. Read the `x-levanta-hmac-sha256` header from the given request.

  2. Create a sha-256 hash of the full request body sent by Levanta using the webhook secret key

  3. Encode the sha-256 hash into hex

  4. Compare the generated hex code with the header given by Levanta; if they match, your request is verified.

Here’s some example code in Node.js:

import { createHmac, timingSafeEqual } from 'crypto';
import { IncomingMessage } from 'http';
import { buffer } from 'micro';

const LEVANTA_WEBHOOK_SECRET = 'test-secret';

const verifyLevantaWebhook = async (req: IncomingMessage) => {
const rawRequestBody = await buffer(req);
const levantaHmacHeader = req.headers['x-levanta-hmac-sha256'];
const signature = createHmac('sha256', LEVANTA_WEBHOOK_SECRET).update(rawRequestBody).digest('hex');
const trusted = Buffer.from(signature, 'utf-8');
const untrusted = Buffer.from(levantaHmacHeader, 'utf-8');
return timingSafeEqual(trusted, untrusted);
};

### Event Documentation

###
link.disabled

This event is sent whenever a previously active link has been disabled. This can happen when a brand removes a product from the Levanta marketplace or has left Levanta altogether. It may also occur when a Creator manually disables a link.

Payload:

{
"id": "f389f591-605b-414a-a723-91facb51496d",
"type": "link.disabled",
"created": 1697129696444,
"version": "1.0.0",
"data": {
"id": "lv_test_M46DpmeyOqlpzWihYO",
"url": "https://amazon.com/dp/B0BCYQL76Z?maas=maas_adg_api_92bb60a2-b343-4f3b-8e19-91edabf8d162_static_9_129&ref_=aa_maas&tag=maas&aa_campaignid=lv_test_jFQX40OTtAmtuDRdz2&aa_adgroupid=lv_test_M46DpmeyOqlpzWihYO&aa_creativeid=lv_test_3Lzv1xNujctNkMU2Ie&m=e113ee5e-e7ee-4351-8786-e70fe5af3f1f",
"active": false,
"object": "link",
"sourceId": "my-source-id...",
"sourceName": "my-source-name...",
"sourceSubId": "my-sub-id..."
}
}

### product.access.gained

This event is sent when you gain access to a product. This means you are able to create a link for the product.

Payload:

{
"id": "f389f591-605b-414a-a723-91facb51496d",
"type": "product.added",
"created": 1697129696444,
"version": "1.0.0"
"data": {
"object": "product",
"asin": "AAAAAAAAAA",
"marketplace": "amazon.com",
"commission": 0.10,
"pricing": {
"currency": "USD",
"price": 10.99,
},
}
}

###
product.removed

This event is sent when a product is removed from the Levanta catalog. You may or may not have access to it.

Payload:

{
"id": "f389f591-605b-414a-a723-91facb51496d",
"type": "product.removed",
"created": 1697129696444,
"version": "1.0.0"
"data": {
"object": "product",
"asin": "AAAAAAAAAA",
"marketplace": "amazon.com",
"commission": 0.10,
"pricing": {
"currency": "USD",
"price": 10.99,
},
}
}

Related Articles

[More Details on the Creator API](/articles/8533560164-more-details-on-the-creator-api) [Creator API Documentation](/articles/7230114691-creator-api-documentation)

---

<a id="2"></a>

## 2. More Details on the Creator API

**Source:** <https://knowledge.levanta.io/articles/8533560164-more-details-on-the-creator-api>

# More Details on the Creator API

Last updated 1 year ago

### Prerequisites

To gain access to the _Levanta Creator API,_ you must have completed the following steps:

  1. Gained access to a creator account by either:

     1. Creating a creator account at [app.levanta.io/auth/sign-up](https://app.levanta.io/auth/sign-up)

     2. Being invited to a creator account by a team member

  2. Gained API access by requesting an API key via our in-app chatbot located in the lower-right corner of your screen when signed in

     1. It may take up to a week to be granted access to the api

     2. After being granted an api key, you can access it [here](https://app.levanta.io/creator/settings/api) when signed in as an admin for your creator team

### Playground

Access Swagger documentation, where you can test out the endpoints [here](https://app.levanta.io/creator/api-docs) (must be signed in).

### Authorization

All requests to the Creator API must be made with an API key. You can check if you have an API key [here](https://app.levanta.io/creator/settings/api) when logged into an admin account.

All requests made to <https://app.levanta.io/api/creator/v1> should be made with the Authorization header set to “Bearer <**API-Key** >”

### Pagination

All of our paginated endpoints use cursor-based pagination and accept a parameter named “cursor”. The first call to the endpoint can omit “cursor”. Every call to an endpoint will return “cursor” in its JSON response, which should be passed as the value for “cursor” in the next call. If there are no more items to paginate through cursor will be returned as null.

### Endpoint Documentation

**GET:**

  * [/brands](https://www.notion.so/levanta/brands-2e29ff7fc67949b789d4e1c07031346e)

  * [/brands/storefronts](https://www.notion.so/levanta/brands-storefronts-cd834919c91f4d1da0c86b4c18acd8e4)

  * [/products](https://www.notion.so/levanta/products-839f12d4d0224904a57b452cf6d4d6ac)

  * [/products/{asin}](https://www.notion.so/levanta/products-asin-eb0099c60691416faccffd0ac63a8a29)

  * [/products/{marketplace}/{asin}](https://www.notion.so/levanta/products-marketplace-asin-609599eef7a84effbef094bed7b3d56f)

  * [/deals](https://www.notion.so/levanta/deals-b7c666a1e1aa428db5b4ad167f125003)

  * [/links/{link_id}](https://www.notion.so/levanta/links-link_id-38fcd3426c31488f8330f8be56a3fb17)

  * [/links](https://www.notion.so/levanta/links-0f78fbbdeba0439783737e7eeb3a13e4)

  * [/links/storefronts](https://www.notion.so/levanta/links-storefronts-fa02773890ff4099b00bb89b61d13439)

  * [/reports](https://www.notion.so/levanta/reports-3ac989ea7505435eaba3e19c35c0c8ef)

  * [/reports/clicks](https://www.notion.so/levanta/reports-clicks-3b5cef34d5834e65978e8361f81fc2db)

  * [/invoices/items](https://www.notion.so/levanta/invoices-items-04c4b35723634108816e76ef09b1591a)

**POST** :

  * [/links](https://www.notion.so/levanta/links-386d5ea5e6aa4451ba8673114427bbda)

  * [/links/storefront](https://www.notion.so/levanta/links-storefront-0ecde26d2a3f43f58de1a190fe1b765d)

  * [/links/storefront/{storefront_id}](https://www.notion.so/levanta/links-storefront-storefront_id-62c56a58224347048674d7c88cd72960)

### Benefits of the Levanta API for Publishers

The Levanta API unlocks a host of advantages for publishers, affiliates, and creators, including:

  1. Streamlined Integration: Integrate your existing technology with Levanta, instantly opening up hundreds of thousands of promotional opportunities via direct partnerships with Amazon Sellers.

  2. Customizable Reporting: Get access to tailored performance reports, offering insights into clicks, conversions, estimated sales, and estimated commissions for each link. With this data, you can better understand and optimize your promotional strategies.

  3. Simplified Product Discovery: The API’s extensive filtering options make it easier than ever to discover relevant products from your partnered brands, streamlining your affiliate opportunity discovery process.

  4. Link Creation & Management: Unlock a host of use cases with programmatic access to affiliate link creation and management.

### Levanta API Key Features

  1. Active Brands Endpoint (/partners): Discover brand names and IDs with whom you have active partnerships. This feature allows you to easily navigate through your brand connections, ensuring you stay up to date with current collaborations.

  2. Product Catalog Endpoint (/products): Access the Levanta product catalog, sorting by title, commission, or price. The API enables you to filter by ASINs, brand IDs, access, minimum/maximum commission, and stock availability, streamlining your product search and selection process.

  3. Product and Link Reporting Endpoints (/reports): Stay informed on your link performance and product reports within a given date range, filtering by ASINs, sources, and brand IDs. This API functionality provides you with valuable insights into your marketing performance, allowing you to make data-driven decisions for optimizing your promotional efforts.

  4. Link Creation and Management Endpoints (/links): Easily create and manage your unique tracking links by ASIN/source pairs and filter by ASIN/source/adGroupId.

### Example of a Common API Integration

Below is an example of how publisher partners typically integrate via the Levanta API:

  * Run a scheduled job that uses our GET /products endpoint (with access=true) to maintain a database of all Levanta ASINs. “access=true” ensures you are getting a list of ASINs you have access to by being part of the brand’s program

  * Whenever a new Amazon link is found on your platform or site/s, check the ASIN against your Levanta ASIN database

  * When matches are identified, use our POST /links endpoint to create your unique Levanta link

  * You can utilize the Source functionality to segment ASIN performance at a more granular level (e.g. per platform, site, or article). By passing an ID to the Source field, the API will return a unique link for that specific ASIN-Source combination

  * Use our GET /reports endpoint to get daily performance reports per unique link/source. This will include clicks, add-to-carts, conversions, sales, and commissions

❗Note:

  * Make sure to check for “access=true” for the /products endpoint to avoid pulling in ASINs you do not have access to yet

  * Make sure to occasionally check if your links have been disabled, or set up a webhook to keep track of them

  * Be careful when modifying link parameters in any way, as it can easily break tracking

When might this be the best solution for you?

  * This works best for affiliates, publishers, and creators who prefer a dynamic and automated process of ASIN matching, link creation, and reporting

  * If you have numerous ASINs to monetize through Levanta and you don’t already work with tech partners (see below), this is the most scalable and seamless option

Related Articles

[Creator API Documentation](/articles/7230114691-creator-api-documentation) [Creator Webhooks](/articles/3588852646-creator-webhooks)

---

<a id="3"></a>

## 3. Creator API Documentation

**Source:** <https://knowledge.levanta.io/articles/7230114691-creator-api-documentation>

# Creator API Documentation

Last updated 1 year ago

## The Levanta API enables a wide range of use cases and unlocks the ability to programmatically implement Levanta affiliate links across content, enabling Creators to scale out direct partnerships with Amazon sellers.

[**View Creator API**](https://api-docs.levanta.io/introduction)

Related Articles

[More Details on the Creator API](/articles/8533560164-more-details-on-the-creator-api) [Creator Webhooks](/articles/3588852646-creator-webhooks)

---

# Seller API

<a id="4"></a>

## 4. More Details on the Seller API

**Source:** <https://knowledge.levanta.io/articles/2817589603-more-details-on-the-seller-api>

# More Details on the Seller API

Last updated 1 year ago

### Prerequisites

To gain access to the _Levanta Seller API,_ you must have completed the following steps:

  1. Gained access to a seller account by either:

     1. Creating a seller account at [app.levanta.io/auth/sign-up](https://app.levanta.io/auth/sign-up)

     2. Being invited to a seller account by a team member

  2. Gained API access by generating an API key at [/seller/settings/api](https://app.levanta.io/seller/settings/api)

     * Must be signed into an admin account to be able to do this

     * Simply click the green “Generate API Key” button

### Playground

Access Swagger documentation, where you can test out the endpoints [here](https://api-docs.levanta.io/introduction).

### Authorization

All requests to the Seller API must be made with an API key. You can check if you have an API key [here](https://app.levanta.io/creator/settings/api) when logged into an account with admin permissions.

All requests made to <https://app.levanta.io/api/seller/v1> should be made with the Authorization header set to “Bearer <**API-Key** >”

### Pagination

All of our paginated endpoints use cursor-based pagination and accept a parameter named “cursor”. The first call to the endpoint can omit “cursor”. Every call to an endpoint will return “cursor” in its JSON response, which should be passed as the value for “cursor” in the next call. If there are no more items to paginate through cursor will be returned as null.

### Endpoint Documentation

**GET** :

  * [/creators/active](https://www.notion.so/creators-active-3bac3a10d1e24fa8af162b205f91c4d2?pvs=21)

  * [/brands/{brand_id}](https://www.notion.so/brands-brand_id-6141782076c74c5ca616f46e350f6dc6?pvs=21)

  * [/brands](https://www.notion.so/brands-7948491a8f544d56a298dda20c405ce8?pvs=21)

  * [/reports](https://www.notion.so/reports-56f90099ef364293b278890521935860?pvs=21)

  * [/reports/brb](https://www.notion.so/reports-brb-a028c8a3ebb242f2a9b71c4a614f3789?pvs=21)

  * [/reports/clicks](https://www.notion.so/reports-clicks-36549dc3690f4d00b05e964b535f0b5d?pvs=21)

  * [/products](https://www.notion.so/products-4566b3c8ce3b45d083aea8ebaf78f579?pvs=21)

Related Articles

[Seller API Documentation](/articles/9228896098-seller-api-documentation)

---

<a id="5"></a>

## 5. Seller API Documentation

**Source:** <https://knowledge.levanta.io/articles/9228896098-seller-api-documentation>

# Seller API Documentation

Last updated 16 days ago

## The Levanta API enables a wide range of use cases and unlocks the ability to programmatically implement Levanta affiliate links across content, enabling Creators to scale out direct partnerships with Amazon sellers.

[**View Seller API**](https://api-docs.levanta.io/v2/seller/brands/get-brand-by-id)

Related Articles

[More Details on the Seller API](/articles/2817589603-more-details-on-the-seller-api)

---

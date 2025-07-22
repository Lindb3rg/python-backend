Table product {
  id serial [pk, increment]
  name varchar(255) [not null]
  category varchar(255) [not null]
  created_at timestamp [default: `CURRENT_TIMESTAMP`]
  updated_at timestamp [default: `CURRENT_TIMESTAMP`]
}

Table order {
  id serial [pk, increment]
  customer_name varchar(100) [not null]
  customer_email varchar(100) [not null]
  order_date date
  status varchar(100) [not null]
  created_at timestamp [default: `CURRENT_TIMESTAMP`]
}

Table order_details {
  id serial [pk, increment]
  product_id integer [ref: > product.id]
  order_id integer [ref: > order.id]
  quantity smallint [not null]
  unit_price real [not null]
  subtotal real [not null]
}

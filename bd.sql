CREATE SCHEMA IF NOT EXISTS `shop` DEFAULT CHARACTER SET utf8 ;
USE `shop` ;

CREATE TABLE IF NOT EXISTS `shop`.`Category` (
  `category_number` INT NOT NULL,
  `category_name` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`category_number`),
  UNIQUE INDEX `category_number_UNIQUE` (`category_number` ASC) VISIBLE)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `shop`.`Product` (
  `id_product` INT NOT NULL,
  `category_number` INT NOT NULL,
  `product_name` VARCHAR(50) NOT NULL,
  `characteristics` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id_product`),
  INDEX `category_name_idx` (`category_number` ASC) VISIBLE,
  UNIQUE INDEX `id_product_UNIQUE` (`id_product` ASC) VISIBLE,
  CONSTRAINT `category_number`
    FOREIGN KEY (`category_number`)
    REFERENCES `shop`.`Category` (`category_number`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `shop`.`Store_Product` (
  `UPC` VARCHAR(12) NOT NULL,
  `UPC_prom` VARCHAR(12) NULL,
  `id_product` INT NOT NULL,
  `selling_price` DECIMAL(13,4) NOT NULL,
  `products_number` INT NOT NULL,
  `promotional_product` TINYINT(1) NOT NULL,
  PRIMARY KEY (`UPC`),
  INDEX `UPC_prom_idx` (`UPC_prom` ASC) VISIBLE,
  INDEX `id_product_idx` (`id_product` ASC) VISIBLE,
  UNIQUE INDEX `UPC_UNIQUE` (`UPC` ASC) VISIBLE,
  CONSTRAINT `UPC_prom`
    FOREIGN KEY (`UPC_prom`)
    REFERENCES `shop`.`Store_Product` (`UPC`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT `id_product`
    FOREIGN KEY (`id_product`)
    REFERENCES `shop`.`Product` (`id_product`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `shop`.`Employee` (
  `id_employee` VARCHAR(10) NOT NULL,
  `empl_surname` VARCHAR(50) NOT NULL,
  `empl_name` VARCHAR(50) NOT NULL,
  `empl_patronymic` VARCHAR(50) NULL,
  `empl_role` VARCHAR(10) NOT NULL,
  `salary` DECIMAL(13,4) NOT NULL,
  `date_of_birth` DATE NOT NULL,
  `date_of_start` DATE NOT NULL,
  `phone_number` VARCHAR(13) NOT NULL,
  `city` VARCHAR(50) NOT NULL,
  `street` VARCHAR(50) NOT NULL,
  `zip_code` VARCHAR(9) NOT NULL,
  `login` VARCHAR(15) NOT NULL,
  `password` VARCHAR(128) NOT NULL,
  PRIMARY KEY (`id_employee`, `login`),
  UNIQUE INDEX `id_employee_UNIQUE` (`id_employee` ASC) VISIBLE,
  UNIQUE INDEX `login_UNIQUE` (`login` ASC) VISIBLE)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `shop`.`Customer_Card` (
  `card_number` VARCHAR(13) NOT NULL,
  `customer_surname` VARCHAR(50) NOT NULL,
  `cust_name` VARCHAR(50) NOT NULL,
  `cust_patronymic` VARCHAR(50) NULL,
  `phone_number` VARCHAR(13) NOT NULL,
  `city` VARCHAR(50) NULL,
  `street` VARCHAR(50) NULL,
  `zip_code` VARCHAR(9) NULL,
  `percent` INT NOT NULL,
  PRIMARY KEY (`card_number`),
  UNIQUE INDEX `card_number_UNIQUE` (`card_number` ASC) VISIBLE)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `shop`.`Bill` (
  `check_number` VARCHAR(10) NOT NULL,
  `id_employee` VARCHAR(10) NOT NULL,
  `card_number` VARCHAR(13) NULL,
  `print_date` DATETIME NOT NULL,
  `sum_total` DECIMAL(13,4) NOT NULL,
  `vat` DECIMAL(13,4) NOT NULL,
  PRIMARY KEY (`check_number`),
  INDEX `id_employee_idx` (`id_employee` ASC) VISIBLE,
  INDEX `card_number_idx` (`card_number` ASC) VISIBLE,
  UNIQUE INDEX `check_number_UNIQUE` (`check_number` ASC) VISIBLE,
  CONSTRAINT `id_employee`
    FOREIGN KEY (`id_employee`)
    REFERENCES `shop`.`Employee` (`id_employee`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE,
  CONSTRAINT `card_number`
    FOREIGN KEY (`card_number`)
    REFERENCES `shop`.`Customer_Card` (`card_number`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `shop`.`Sale` (
  `UPC` VARCHAR(12) NOT NULL,
  `check_number` VARCHAR(10) NOT NULL,
  `product_number` INT NOT NULL,
  `selling_price` DECIMAL(13,4) NOT NULL,
  PRIMARY KEY (`UPC`, `check_number`),
  INDEX `check_number_idx` (`check_number` ASC) VISIBLE,
  CONSTRAINT `UPC`
    FOREIGN KEY (`UPC`)
    REFERENCES `shop`.`Store_Product` (`UPC`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE,
  CONSTRAINT `check_number`
    FOREIGN KEY (`check_number`)
    REFERENCES `shop`.`Bill` (`check_number`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

USE `shop` ;

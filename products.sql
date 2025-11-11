USE rowdys_closet_db;

DELETE FROM products;

INSERT INTO products (price, size, name, stock, type, description , img_file_path)
VALUES
    (42.00, "Large", "UTSA Roadrunnner Head Hoodie", 35, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Roadrunnner_Head_Hoodie.png"),
    (42.00, "Large", "UTSA Hoodie", 25, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Hoodie.png"),
    (42.00, "Large", "UTSA Football Verticle Hoodie", 25, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Football_Vertical_Hoodie.png"),
    (42.00, "Large", "UTSA Hoodie", 25, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Hoodie.png"),
    (42.00, "Large", "UTSA Ugly Christmas Sweater", 25, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Ugly_Christmas_Sweater.png"),
    (42.00, "Large", "UTSA Roadrunner Head - Full Zip Hoodie", 25, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Roadrunner_Head_-_Full_Zip_Hoodie.png"),
    (57.00, "Large", "UTSA Full Mascot Vintage Sweatshirt", 25, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Full_Mascot_Vintage_Sweater.png"),
    (57.00, "Large", "UTSA Script Vintage", 25, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Script_Vintage.png"),
    (58.00, "Large", "UTSA Softshell Core Vest", 25, "Jackets", "Jackets", "/static/img/product_images/UTSA_Softshell_Core_Vest.png"),
    (68.00, "Large", "UTSA Black Charger Jacket", 25, "Jackets", "Jackets", "/static/img/product_images/UTSA_Black_Charger_Jacket.png"),
    (64.00, "Large", "UTSA Black Softshell Jacket", 25, "Jackets", "Jackets", "/static/img/product_images/UTSA_Black_Softshell_Jacket.png"),
    (155.00, "Large", "UTSA Black Heather Jacket", 25, "Jackets", "Jackets", "/static/img/product_images/UTSA_Black_Heather_Jacket.png"),
    (310.00, "Large", "UTSA Black Thermoball Trekker Jacket", 15, "Jackets", "Jackets", "/static/img/product_images/UTSA_Black_Thermoball_Trekker_Jacket.png"),
    (230.00, "Large", "UTSA Black Apex Barrier Softwhell Jacket", 25, "Jackets", "Jackets", "/static/img/product_images/UTSA_Black_Apex_Barrier_Softwhell_Jacket.png"),
    (57.00, "Large", "UTSA Sport Tek Sport Wick Stretch Jacket", 25, "Jackets", "Jackets", "/static/img/product_images/UTSA_Sport_Tek_Sport_Wick_Stretch_Jacket.png"),
    (170.00, "Large", "UTSA Black Vortex Waterproof 3 in 1 Jacket", 25, "Jackets", "Jackets", "/static/img/product_images/UTSA_Black_Vortex_Waterproof_3_in_1_Jacket.png"),
    (22.00, "Large", "UTSA Roadrunner Head T-Shirt", 25, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Roadrunner_Head_T-Shirt.png"),
    (22.00, "Large", "UTSA Logo T-Shirt", 25, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Logo_T-Shirt.png"),
    (22.00, "Large", "UTSA Roadrunner Arched T-Shirt", 25, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Roadrunner_Arched_T-Shirt.png"),
    (22.00, "Large", "UTSA Ugly Christmas T-Shirt", 25, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Ugly_Christmas_T-Shirt.png"),
    (22.00, "Large", "UTSA Women's Basketball Runners T-Shirt", 25, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Womens_Basketball_Runners_T-Shirt.png"),
    (22.00, "Large", "UTSA Fifteenth T-Shirt", 25, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Fifteenth_T-Shirt.png"),
    (22.00, "Large", "UTSA Baseball T-Shirt", 25, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Baseball_T-Shirt.png"),
    (22.00, "Large", "UTSA Performance Tee", 25, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Performance_Tee.png"),
    (42.00, "Medium", "UTSA Roadrunnner Head Hoodie", 35, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Roadrunnner_Head_Hoodie.png"),
    (42.00, "Medium", "UTSA Hoodie", 25, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Hoodie.png"),
    (42.00, "Medium", "UTSA Football Verticle Hoodie", 25, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Football_Vertical_Hoodie.png"),
    (42.00, "Medium", "UTSA Hoodie", 25, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Hoodie.png"),
    (42.00, "Medium", "UTSA Ugly Christmas Sweater", 25, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Ugly_Christmas_Sweater.png"),
    (42.00, "Medium", "UTSA Roadrunner Head - Full Zip Hoodie", 50, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Roadrunner_Head_-_Full_Zip_Hoodie.png"),
    (57.00, "Medium", "UTSA Full Mascot Vintage Sweatshirt", 50, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Full_Mascot_Vintage_Sweater.png"),
    (57.00, "Medium", "UTSA Script Vintage", 50, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Script_Vintage.png"),
    (58.00, "Medium", "UTSA Softshell Core Vest", 25, "Jackets", "Jackets", "/static/img/product_images/UTSA_Softshell_Core_Vest.png"),
    (68.00, "Medium", "UTSA Black Charger Jacket", 25, "Jackets", "Jackets", "/static/img/product_images/UTSA_Black_Charger_Jacket.png"),
    (64.00, "Medium", "UTSA Black Softshell Jacket", 25, "Jackets", "Jackets", "/static/img/product_images/UTSA_Black_Softshell_Jacket.png"),
    (155.00, "Medium", "UTSA Black Heather Jacket", 25, "Jackets", "Jackets", "/static/img/product_images/UTSA_Black_Heather_Jacket.png"),
    (310.00, "Medium", "UTSA Black Thermoball Trekker Jacket", 40, "Jackets", "Jackets", "/static/img/product_images/UTSA_Black_Thermoball_Trekker_Jacket.png"),
    (230.00, "Medium", "UTSA Black Apex Barrier Softwhell Jacket", 45, "Jackets", "Jackets", "/static/img/product_images/UTSA_Black_Apex_Barrier_Softwhell_Jacket.png"),
    (57.00, "Medium", "UTSA Sport Tek Sport Wick Stretch Jacket", 60, "Jackets", "Jackets", "/static/img/product_images/UTSA_Sport_Tek_Sport_Wick_Stretch_Jacket.png"),
    (170.00, "Medium", "UTSA Black Vortex Waterproof 3 in 1 Jacket", 70, "Jackets", "Jackets", "/static/img/product_images/UTSA_Black_Vortex_Waterproof_3_in_1_Jacket.png"),
    (22.00, "Medium", "UTSA Roadrunner Head T-Shirt", 75, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Roadrunner_Head_T-Shirt.png"),
    (22.00, "Medium", "UTSA Logo T-Shirt", 95, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Logo_T-Shirt.png"),
    (22.00, "Medium", "UTSA Roadrunner Arched T-Shirt", 60, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Roadrunner_Arched_T-Shirt.png"),
    (22.00, "Medium", "UTSA Ugly Christmas T-Shirt", 55, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Ugly_Christmas_T-Shirt.png"),
    (22.00, "Medium", "UTSA Women's Basketball Runners T-Shirt", 55, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Womens_Basketball_Runners_T-Shirt.png"),
    (22.00, "Medium", "UTSA Fifteenth T-Shirt", 45, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Fifteenth_T-Shirt.png"),
    (22.00, "Medium", "UTSA Baseball T-Shirt", 20, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Baseball_T-Shirt.png"),
    (22.00, "Medium", "UTSA Performance Tee", 20, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Performance_Tee.png"),
    (42.00, "Small", "UTSA Roadrunnner Head Hoodie", 35, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Roadrunnner_Head_Hoodie.png"),
    (42.00, "Small", "UTSA Hoodie", 30, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Hoodie.png"),
    (42.00, "Small", "UTSA Football Verticle Hoodie", 85, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Football_Vertical_Hoodie.png"),
    (42.00, "Small", "UTSA Hoodie", 80, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Hoodie.png"),
    (42.00, "Small", "UTSA Ugly Christmas Sweater", 50, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Ugly_Christmas_Sweater.png"),
    (42.00, "Small", "UTSA Roadrunner Head - Full Zip Hoodie", 25, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Roadrunner_Head_-_Full_Zip_Hoodie.png"),
    (57.00, "Small", "UTSA Full Mascot Vintage Sweatshirt", 35, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Full_Mascot_Vintage_Sweater.png"),
    (57.00, "Small", "UTSA Script Vintage", 90, "Hoodies", "Hoodies", "/static/img/product_images/UTSA_Script_Vintage.png"),
    (58.00, "Small", "UTSA Softshell Core Vest", 35, "Jackets", "Jackets", "/static/img/product_images/UTSA_Softshell_Core_Vest.png"),
    (68.00, "Small", "UTSA Black Charger Jacket", 70, "Jackets", "Jackets", "/static/img/product_images/UTSA_Black_Charger_Jacket.png"),
    (64.00, "Small", "UTSA Black Softshell Jacket", 60, "Jackets", "Jackets", "/static/img/product_images/UTSA_Black_Softshell_Jacket.png"),
    (155.00, "Small", "UTSA Black Heather Jacket", 65, "Jackets", "Jackets", "/static/img/product_images/UTSA_Black_Heather_Jacket.png"),
    (310.00, "Small", "UTSA Black Thermoball Trekker Jacket", 40, "Jackets", "Jackets", "/static/img/product_images/UTSA_Black_Thermoball_Trekker_Jacket.png"),
    (230.00, "Small", "UTSA Black Apex Barrier Softwhell Jacket", 50, "Jackets", "Jackets", "/static/img/product_images/UTSA_Black_Apex_Barrier_Softwhell_Jacket.png"),
    (57.00, "Small", "UTSA Sport Tek Sport Wick Stretch Jacket", 50, "Jackets", "Jackets", "/static/img/product_images/UTSA_Sport_Tek_Sport_Wick_Stretch_Jacket.png"),
    (170.00, "Small", "UTSA Black Vortex Waterproof 3 in 1 Jacket", 75, "Jackets", "Jackets", "/static/img/product_images/UTSA_Black_Vortex_Waterproof_3_in_1_Jacket.png"),
    (22.00, "Small", "UTSA Roadrunner Head T-Shirt", 25, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Roadrunner_Head_T-Shirt.png"),
    (22.00, "Small", "UTSA Logo T-Shirt", 25, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Logo_T-Shirt.png"),
    (22.00, "Small", "UTSA Roadrunner Arched T-Shirt", 30, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Roadrunner_Arched_T-Shirt.png"),
    (22.00, "Small", "UTSA Ugly Christmas T-Shirt", 35, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Ugly_Christmas_T-Shirt.png"),
    (22.00, "Small", "UTSA Women's Basketball Runners T-Shirt", 40, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Womens_Basketball_Runners_T-Shirt.png"),
    (22.00, "Small", "UTSA Fifteenth T-Shirt", 40, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Fifteenth_T-Shirt.png"),
    (22.00, "Small", "UTSA Baseball T-Shirt", 15, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Baseball_T-Shirt.png"),
    (22.00, "Small", "UTSA Performance Tee", 65, "T-Shirts", "T-Shirts", "/static/img/product_images/UTSA_Performance_Tee.png"),
    (18.00, NULL, "Brushed Bull Denim Visor 210", 55, "Headwear", "Headwear", "/static/img/product_images/Brushed_Bull_Denim_Visor_210.png"),
    (21.00, NULL, "Structured Adjustable Pro Style Hat - Mascot", 45, "Headwear", "Headwear", "/static/img/product_images/Structured_Adjustable_Pro_Style_Hat_-_Mascot.png"),
    (21.00, NULL, "Mountain Beanie - UTSA Roadrunner Head - Institutional Mark", 15, "Headwear", "Headwear", "/static/img/product_images/Mountain_Beanie_-_UTSA_Roadrunner_Head.png"),
    (32.00, NULL, "Mountain Beanie - UTSA Roadrunner Head", 20, "Headwear", "Headwear", "/static/img/product_images/Mountain_Beanie_-_UTSA_Roadrunner_Head.png"),
    (45.00, NULL, "Knit Beanie w:Cuff - UTSA Roadrunner Head", 55, "Headwear", "Headwear", "/static/img/product_images/Knit_Beanie_Cuff_-_UTSA_Roadrunner_Head.png"),
    (15.00, NULL, "Sportsman Pom Pom Cuffed Beanie", 45, "Headwear", "Headwear", "/static/img/product_images/Sportsman_Pom_Pom_Cuffed_Beanie.png"),
    (82.00, NULL, "Black Roam Lite Backpack", 30, "Bags", "Bags", "/static/img/product_images/Black_Roam_Lite_Backpack.png");


SELECT * FROM products


UPDATE products
SET stock = 0
WHERE name = "UTSA Roadrunnner Head Hoodie";














-- Insert all products

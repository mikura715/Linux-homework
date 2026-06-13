SET NAMES utf8mb4;
CREATE DATABASE IF NOT EXISTS shop_mall DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE shop_mall;

CREATE TABLE `user` (
  user_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  email VARCHAR(100),
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `goods` (
  goods_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  goods_name VARCHAR(200) NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  stock INT NOT NULL DEFAULT 0,
  category VARCHAR(50),
  description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `cart` (
  cart_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  goods_id BIGINT NOT NULL,
  buy_num INT NOT NULL DEFAULT 1,
  FOREIGN KEY(user_id) REFERENCES `user`(user_id),
  FOREIGN KEY(goods_id) REFERENCES goods(goods_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 重点修复：order_id改为VARCHAR(36)适配uuid4
CREATE TABLE `orders` (
  order_id VARCHAR(36) PRIMARY KEY,
  user_id BIGINT NOT NULL,
  total_amount DECIMAL(10,2) NOT NULL,
  status TINYINT COMMENT '0待发货 1已发货 2已完成',
  address TEXT,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES `user`(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE order_item (
  item_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  order_id VARCHAR(36) NOT NULL,
  goods_id BIGINT NOT NULL,
  num INT NOT NULL,
  single_price DECIMAL(10,2) NOT NULL,
  FOREIGN KEY(order_id) REFERENCES orders(order_id),
  FOREIGN KEY(goods_id) REFERENCES goods(goods_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 预置测试账号：用户名test，密码123456
INSERT INTO `user`(username,password_hash,email) VALUES('test','123456','test@shop.com');

-- 10个分类，每类5件，合计50件商品
INSERT INTO goods(goods_name,price,stock,category,description)
VALUES
-- 1.服饰
('夏季纯棉短袖T恤',59.90,300,'服饰','宽松透气百搭日常上衣'),
('薄款连帽运动卫衣',89.00,240,'服饰','春秋休闲宽松外套'),
('弹力修身牛仔长裤',129.00,180,'服饰','百搭直筒显瘦牛仔裤'),
('简约纯棉长袖衬衫',75.00,200,'服饰','通勤商务休闲衬衣'),
('轻薄防晒冰丝外套',99.00,160,'服饰','夏季防紫外线薄开衫'),
-- 2.数码
('主动降噪无线蓝牙耳机',199.00,120,'数码','低延迟长续航音乐耳机'),
('20W快充充电适配器',49.00,500,'数码','兼容手机平板快充'),
('迷你便携蓝牙小音箱',139.00,90,'数码','户外防水小型音响'),
('高清Type-C数据线',29.90,600,'数码','快充耐用编织线'),
('桌面手机无线充电器',79.00,150,'数码','兼容安卓苹果无线快充'),
-- 3.护肤
('高保湿修护面霜',89.00,220,'护肤','干皮补水滋润修护'),
('清爽控油氨基酸洗面奶',45.00,350,'护肤','油皮深层清洁洁面'),
('玻尿酸补水面膜10片装',79.00,280,'护肤','舒缓干燥提亮肤色'),
('无色保湿润唇膏',29.90,700,'护肤','秋冬防干裂护唇'),
('清爽保湿爽肤水',65.00,200,'护肤','平衡水油补水打底'),
-- 4.家居日用
('加厚纯棉洗脸毛巾',19.90,800,'家居日用','吸水柔软不掉毛'),
('大容量密封保鲜盒三件套',39.90,320,'家居日用','冰箱食物收纳保鲜'),
('可折叠脏衣收纳篮',25.90,400,'家居日用','衣物杂物整理收纳'),
('硅胶隔热防烫锅垫',12.90,900,'家居日用','餐桌厨具隔热防护'),
('简约桌面纸巾抽纸盒',16.90,550,'家居日用','客厅卧室桌面收纳'),
-- 5.零食茶饮
('奶香酥脆曲奇饼干礼盒',45.00,260,'零食茶饮','下午茶点心礼盒'),
('独立包装原味坚果混合装',69.00,200,'零食茶饮','每日坚果健康代餐'),
('冻干柠檬片泡水花茶',29.90,380,'零食茶饮','维C花果养生茶'),
('速溶拿铁咖啡30条装',59.00,220,'零食茶饮','办公提神速溶咖啡'),
('蜂蜜柚子茶玻璃罐装',35.00,300,'零食茶饮','冲水果味甜茶'),
-- 6.运动户外
('速干透气运动短袖',69.00,240,'运动户外','跑步健身排汗上衣'),
('高弹力防滑瑜伽垫',89.00,180,'运动户外','健身瑜伽减震垫子'),
('轻便折叠遮阳防晒帽',39.90,350,'运动户外','户外出行防紫外线'),
('弹力负重健身束带',29.90,420,'运动户外','力量训练辅助器材'),
('便携大容量运动水杯',45.00,300,'运动户外','健身骑行防漏水杯'),
-- 7.美妆彩妆
('哑光雾面丝绒口红',69.00,220,'美妆彩妆','持久显色不拔干'),
('轻薄透气气垫BB霜',99.00,160,'美妆彩妆','遮瑕提亮底妆'),
('纤细防水眼线液笔',35.00,400,'美妆彩妆','持久不晕染眼线'),
('自然立体三色眉粉',49.00,320,'美妆彩妆','填充眉毛持久定型'),
('保湿无色妆前隔离乳',59.00,200,'美妆彩妆','打底服帖控油隔离'),
-- 8.图书文具
('加厚A5横线笔记本5本装',25.90,600,'图书文具','学生办公书写本子'),
('按动中性黑色水笔20支装',19.90,900,'图书文具','顺滑耐写签字笔'),
('大号透明文件收纳袋',12.90,750,'图书文具','试卷资料分类收纳'),
('金属简约桌面订书机套装',35.00,300,'图书文具','办公装订订书器'),
('可擦大容量荧光标记笔6色',29.90,450,'图书文具','书本重点标记画笔'),
-- 9.母婴用品
('婴儿纯棉柔软口水巾5条',29.90,500,'母婴用品','新生儿防溢奶围兜'),
('温和无刺激婴儿润肤乳',49.00,320,'母婴用品','宝宝全身保湿护肤'),
('宽口径防胀气婴儿奶瓶',69.00,240,'母婴用品','新生儿喝奶耐摔奶瓶'),
('婴儿防水隔尿垫大号单片',15.90,800,'母婴用品','床品防渗漏护垫'),
('纯棉婴儿连体四季睡衣',79.00,200,'母婴用品','新生儿宽松居家服'),
-- 10.车载用品
('车载手机重力导航支架',39.90,380,'车载用品','出风口稳固导航架'),
('活性炭车载除味竹炭包',19.90,700,'车载用品','车内吸附异味甲醛'),
('高清车载倒车广角摄像头',129.00,140,'车载用品','后视倒车辅助影像'),
('车载快充一拖三数据线',29.90,520,'车载用品','多设备同时充电'),
('简约车载座椅缝隙收纳盒',25.90,400,'车载用品','车内杂物缝隙收纳');
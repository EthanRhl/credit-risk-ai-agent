# scripts/generate_test_data.py
"""
生成模拟测试数据用于项目演示
注意：这些数据仅用于学习和演示，不用于真实业务
"""
import os
import json
import random
from datetime import datetime, timedelta

# 常见姓氏和名字
SURNAMES = ['王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴',
            '徐', '孙', '马', '朱', '胡', '郭', '何', '高', '林', '罗']
NAMES = ['伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '军', '洋',
         '勇', '艳', '杰', '涛', '明', '超', '秀英', '俊', '浩', '宇']

# 常见地址
PROVINCES = ['浙江省', '江苏省', '广东省', '山东省', '河南省', '四川省', '湖北省', '湖南省']
CITIES = ['杭州市', '宁波市', '南京市', '苏州市', '广州市', '深圳市', '成都市', '武汉市']
DISTRICTS = ['西湖区', '上城区', '拱墅区', '滨江区', '余杭区', '萧山区', '江干区', '下城区']
STREETS = ['文三路', '延安路', '解放路', '环城北路', '江南大道', '钱江路', '天目山路', '莫干山路']


def generate_id_number(birth_year, birth_month, birth_day, gender):
    """生成模拟身份证号"""
    area_code = random.choice(['330106', '330102', '330103', '330104', '330105'])
    birth_str = f"{birth_year:04d}{birth_month:02d}{birth_day:02d}"
    seq = random.randint(1, 999)
    gender_bit = seq % 2
    if (gender == '男' and gender_bit == 0) or (gender == '女' and gender_bit == 1):
        seq += 1

    # 校验码计算（简化版，用X代替）
    check_code = random.choice(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'X'])

    return f"{area_code}{birth_str}{seq:03d}{check_code}"


def generate_test_sample(sample_id):
    """生成单个测试样本"""
    # 随机生成年龄（22-55岁，符合信贷主流人群）
    age = random.randint(22, 55)
    birth_year = 2025 - age
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)

    gender = random.choice(['男', '女'])
    surname = random.choice(SURNAMES)
    name = surname + random.choice(NAMES) + random.choice(NAMES)

    ethnicity = random.choice(['汉', '汉', '汉', '汉', '回', '满', '蒙', '壮'])

    address = f"{random.choice(PROVINCES)}{random.choice(CITIES)}{random.choice(DISTRICTS)}{random.choice(STREETS)}{random.randint(1, 999)}号"

    id_number = generate_id_number(birth_year, birth_month, birth_day, gender)

    # 生成模拟语音文本
    loan_amounts = [30000, 50000, 80000, 100000, 150000, 200000]
    loan_purposes = ['装修', '购车', '旅游', '教育', '医疗', '消费', '创业']
    incomes = [5000, 8000, 10000, 15000, 20000, 30000]

    asr_text = f"您好，我想申请一笔{random.choice(loan_amounts)}元的贷款，用于{random.choice(loan_purposes)}。" \
               f"我目前在杭州工作，月收入大约{random.choice(incomes)}元，有稳定的工作和收入来源。" \
               f"希望能尽快审批，谢谢。"

    # 根据条件生成风险标签（用于评估）
    risk_score = 50
    risk_factors = []

    if age < 25:
        risk_score += 20
        risk_factors.append("年龄偏小")
    elif age > 50:
        risk_score += 15
        risk_factors.append("年龄偏大")
    elif 30 <= age <= 45:
        risk_score -= 15
        risk_factors.append("年龄优质")

    if random.choice(incomes) < 8000:
        risk_score += 15
        risk_factors.append("收入偏低")
    elif random.choice(incomes) > 15000:
        risk_score -= 15
        risk_factors.append("收入较高")

    if risk_score >= 70:
        risk_level = "HIGH"
        recommendation = "拒绝"
    elif risk_score >= 40:
        risk_level = "MEDIUM"
        recommendation = "人工复核"
    else:
        risk_level = "LOW"
        recommendation = "通过"

    return {
        "sample_id": sample_id,
        "ocr_fields": {
            "姓名": name,
            "身份证号": id_number,
            "性别": gender,
            "民族": ethnicity,
            "出生日期": f"{birth_year}年{birth_month:02d}月{birth_day:02d}日",
            "住址": address
        },
        "asr_text": asr_text,
        "ground_truth": {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "recommendation": recommendation
        },
        "created_at": datetime.now().isoformat()
    }


def generate_test_dataset(num_samples=50):
    """生成测试数据集"""
    dataset = []
    for i in range(num_samples):
        sample = generate_test_sample(i + 1)
        dataset.append(sample)

    return dataset


if __name__ == "__main__":
    # 生成50个测试样本
    dataset = generate_test_dataset(50)

    # 保存到文件
    output_dir = "assets/test_data"
    os.makedirs(output_dir, exist_ok=True)

    # 保存完整数据集
    with open(os.path.join(output_dir, "test_dataset.json"), "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    # 保存统计信息
    stats = {
        "total_samples": len(dataset),
        "risk_distribution": {
            "HIGH": sum(1 for s in dataset if s["ground_truth"]["risk_level"] == "HIGH"),
            "MEDIUM": sum(1 for s in dataset if s["ground_truth"]["risk_level"] == "MEDIUM"),
            "LOW": sum(1 for s in dataset if s["ground_truth"]["risk_level"] == "LOW")
        },
        "generated_at": datetime.now().isoformat()
    }

    with open(os.path.join(output_dir, "dataset_stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"✓ 已生成 {len(dataset)} 个测试样本")
    print(f"✓ 数据保存至：{output_dir}")
    print(f"✓ 风险分布：HIGH={stats['risk_distribution']['HIGH']}, "
          f"MEDIUM={stats['risk_distribution']['MEDIUM']}, "
          f"LOW={stats['risk_distribution']['LOW']}")
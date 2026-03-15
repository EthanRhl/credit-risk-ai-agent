# scripts/evaluate_model.py
"""
模型效果评估脚本
对比大模型预测结果与真实标签
"""
import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.llm_agent import analyze_risk


def load_test_dataset():
    """加载测试数据集"""
    dataset_path = "assets/test_data/test_dataset.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_prediction(predicted, actual):
    """评估单个预测结果"""
    # 风险等级匹配
    level_match = predicted.get("risk_level") == actual.get("risk_level")

    # 推荐决策匹配
    rec_match = predicted.get("recommendation") == actual.get("recommendation")

    # 风险评分误差（允许±15分误差）
    score_pred = predicted.get("risk_score", 50)
    score_actual = actual.get("risk_score", 50)
    score_diff = abs(score_pred - score_actual)
    score_acceptable = score_diff <= 15

    return {
        "level_correct": level_match,
        "recommendation_correct": rec_match,
        "score_acceptable": score_acceptable,
        "score_diff": score_diff
    }


def run_evaluation():
    """运行完整评估"""
    print("=" * 60)
    print("开始模型效果评估")
    print("=" * 60)

    # 加载测试数据
    dataset = load_test_dataset()
    print(f"加载测试样本：{len(dataset)} 个")

    results = []
    correct_level = 0
    correct_rec = 0
    acceptable_score = 0
    total_score_diff = 0

    for i, sample in enumerate(dataset):
        print(f"\n处理样本 {i + 1}/{len(dataset)}...", end=" ")

        # 调用大模型预测
        prediction_result = analyze_risk(sample["ocr_fields"], sample["asr_text"])

        if prediction_result["status"] == "success":
            predicted = prediction_result["data"]
            actual = sample["ground_truth"]

            eval_result = evaluate_prediction(predicted, actual)
            results.append({
                "sample_id": sample["sample_id"],
                "predicted": predicted,
                "actual": actual,
                "evaluation": eval_result
            })

            # 统计
            if eval_result["level_correct"]:
                correct_level += 1
            if eval_result["recommendation_correct"]:
                correct_rec += 1
            if eval_result["score_acceptable"]:
                acceptable_score += 1
            total_score_diff += eval_result["score_diff"]

            status = "✓" if eval_result["level_correct"] else "✗"
            print(f"{status} 预测:{predicted.get('risk_level')} 实际:{actual.get('risk_level')}")
        else:
            print(f"✗ API调用失败")
            results.append({
                "sample_id": sample["sample_id"],
                "error": prediction_result["message"]
            })

    # 计算评估指标
    total = len(dataset)
    level_accuracy = correct_level / total * 100
    rec_accuracy = correct_rec / total * 100
    score_accept_rate = acceptable_score / total * 100
    avg_score_diff = total_score_diff / total

    # 生成评估报告
    report = {
        "evaluation_time": datetime.now().isoformat(),
        "total_samples": total,
        "metrics": {
            "risk_level_accuracy": f"{level_accuracy:.1f}%",
            "recommendation_accuracy": f"{rec_accuracy:.1f}%",
            "score_acceptable_rate": f"{score_accept_rate:.1f}%",
            "average_score_diff": f"{avg_score_diff:.1f}"
        },
        "summary": {
            "correct_level": correct_level,
            "correct_recommendation": correct_rec,
            "acceptable_score": acceptable_score
        },
        "cost_estimate": f"约 ¥{total * 0.01:.2f}"
    }

    # 保存报告
    report_path = "assets/test_data/evaluation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 打印报告
    print("\n" + "=" * 60)
    print("评估报告")
    print("=" * 60)
    print(f"测试样本数：{total}")
    print(f"风险等级准确率：{level_accuracy:.1f}%")
    print(f"决策建议准确率：{rec_accuracy:.1f}%")
    print(f"评分可接受率：{score_accept_rate:.1f}%")
    print(f"平均评分误差：{avg_score_diff:.1f}")
    print(f"API成本估算：{report['cost_estimate']}")
    print("=" * 60)
    print(f"详细报告已保存至：{report_path}")

    return report


if __name__ == "__main__":
    run_evaluation()
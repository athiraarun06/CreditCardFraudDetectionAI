import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, roc_curve, precision_recall_curve, auc
from sklearn.calibration import calibration_curve


def save_confusion_matrix(y_true, y_pred, out_path, labels=("Legit", "Fraud")):
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(5, 4.5))
    im = ax.imshow(cm, cmap="Purples")
    ax.set_xticks([0, 1]); ax.set_xticklabels(labels)
    ax.set_yticks([0, 1]); ax.set_yticklabels(labels)
    ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
    ax.set_title("Confusion Matrix")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                     color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=14, fontweight="bold")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def save_roc_curve(y_true, y_proba, out_path):
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    roc_auc = auc(fpr, tpr)
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    ax.plot(fpr, tpr, color="#7c3aed", linewidth=2, label=f"ROC curve (AUC = {roc_auc:.3f})")
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray")
    ax.set_xlabel("False Positive Rate"); ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def save_pr_curve(y_true, y_proba, out_path):
    precision, recall, _ = precision_recall_curve(y_true, y_proba)
    pr_auc = auc(recall, precision)
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    ax.plot(recall, precision, color="#2563eb", linewidth=2, label=f"PR curve (AUC = {pr_auc:.3f})")
    ax.set_xlabel("Recall"); ax.set_ylabel("Precision")
    ax.set_title("Precision-Recall Curve")
    ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def save_calibration_curve(y_true, y_proba, out_path, n_bins=10):
    frac_pos, mean_pred = calibration_curve(y_true, y_proba, n_bins=n_bins, strategy="quantile")
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    ax.plot(mean_pred, frac_pos, marker="o", color="#7c3aed", label="Model")
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Perfectly calibrated")
    ax.set_xlabel("Mean Predicted Probability"); ax.set_ylabel("Fraction of Positives")
    ax.set_title("Calibration Curve")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def save_lift_curve(y_true, y_proba, out_path, n_bins=10):
    order = np.argsort(-np.asarray(y_proba))
    y_sorted = np.asarray(y_true)[order]
    n = len(y_sorted)
    bin_size = max(n // n_bins, 1)
    overall_rate = y_sorted.mean() if n > 0 else 0
    lifts, deciles = [], []
    for i in range(n_bins):
        start, end = i * bin_size, (i + 1) * bin_size if i < n_bins - 1 else n
        bucket = y_sorted[start:end]
        if len(bucket) == 0 or overall_rate == 0:
            lifts.append(0)
        else:
            lifts.append(bucket.mean() / overall_rate)
        deciles.append(i + 1)

    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    ax.bar(deciles, lifts, color="#2563eb")
    ax.axhline(1, linestyle="--", color="gray", label="Baseline (no model)")
    ax.set_xlabel("Decile (sorted by predicted risk, highest first)")
    ax.set_ylabel("Lift")
    ax.set_title("Lift Curve")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def generate_all_plots(y_true, y_pred, y_proba, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    save_confusion_matrix(y_true, y_pred, os.path.join(out_dir, "confusion_matrix.png"))
    save_roc_curve(y_true, y_proba, os.path.join(out_dir, "roc_curve.png"))
    save_pr_curve(y_true, y_proba, os.path.join(out_dir, "pr_curve.png"))

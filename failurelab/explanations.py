from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class WeaknessExplanation:
    summary: str
    likely_cause: str
    suggested_action: str
EXPLANATIONS={
"brightness":WeaknessExplanation("Model performance degrades when images become darker.","The model may be overly sensitive to illumination changes or may lack representative low-light training examples.","Add low-light augmentation and representative dark images to the training data, then rerun the stress test."),
"blur":WeaknessExplanation("Model performance degrades when image detail is reduced by blur.","The model may depend heavily on fine textures or sharp edges.","Add blur augmentation and realistic out-of-focus examples during training."),
"compression":WeaknessExplanation("Model performance degrades as JPEG compression increases.","The model may rely on fine visual information that compression removes or distorts.","Train and validate with images saved at multiple JPEG quality levels."),
"occlusion":WeaknessExplanation("Model performance degrades when part of the image is hidden.","The model may rely heavily on a limited visual region rather than distributed evidence across the object.","Add partial-occlusion augmentation and partially visible examples to the training set."),
"rotation":WeaknessExplanation("Model performance degrades when the image is rotated.","The model may have learned orientation-specific features instead of features that remain stable under viewpoint changes.","Introduce realistic rotation augmentation during training and validate across expected camera orientations."),
"crop":WeaknessExplanation("Model performance degrades when image borders are removed.","The model may depend on contextual information near image boundaries or require more of the object to remain visible.","Use crop and scale augmentation and include partially framed objects in the training data."),
}
def explain_weakness(name: str) -> WeaknessExplanation:
    try: return EXPLANATIONS[name]
    except KeyError as exc: raise ValueError(f"No explanation is available for weakness type: {name}") from exc

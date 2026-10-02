from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prepare_photo(input_path, output_path):

    input_path = Path(input_path)
    output_path = Path(output_path)

    print(f"Reading: {input_path}")

    # ---------------------------------------------------------
    # 1. Remove background
    # ---------------------------------------------------------

    print("Removing background...")

    with open(input_path, "rb") as f:
        input_data = f.read()

    output_data = remove(input_data)

    temp_path = output_path.with_name("_no_background.png")

    with open(temp_path, "wb") as f:
        f.write(output_data)

    # ---------------------------------------------------------
    # 2. Read image WITH alpha channel
    # ---------------------------------------------------------

    image = Image.open(temp_path).convert("RGBA")

    rgba = np.array(image)

    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]

    # ---------------------------------------------------------
    # 3. Find the actual subject
    # ---------------------------------------------------------

    print("Finding subject...")

    # Ignore extremely transparent pixels
    mask = alpha > 30

    coords = np.column_stack(
        np.where(mask)
    )

    if coords.size == 0:
        raise RuntimeError(
            "Could not find the subject in the image."
        )

    y_min, x_min = coords.min(axis=0)
    y_max, x_max = coords.max(axis=0)

    print(
        f"Subject bounds: "
        f"x={x_min}:{x_max}, "
        f"y={y_min}:{y_max}"
    )

    # ---------------------------------------------------------
    # 4. Add some padding around the subject
    # ---------------------------------------------------------

    height, width = alpha.shape

    padding_x = int(
        (x_max - x_min) * 0.08
    )

    padding_y = int(
        (y_max - y_min) * 0.05
    )

    x_min = max(
        0,
        x_min - padding_x
    )

    x_max = min(
        width - 1,
        x_max + padding_x
    )

    y_min = max(
        0,
        y_min - padding_y
    )

    y_max = min(
        height - 1,
        y_max + padding_y
    )

    # ---------------------------------------------------------
    # 5. Crop
    # ---------------------------------------------------------

    cropped_rgb = rgb[
        y_min:y_max + 1,
        x_min:x_max + 1
    ]

    cropped_alpha = alpha[
        y_min:y_max + 1,
        x_min:x_max + 1
    ]

    # ---------------------------------------------------------
    # 6. Put subject on white background
    # ---------------------------------------------------------

    white = np.ones_like(
        cropped_rgb,
        dtype=np.uint8
    ) * 255

    alpha_float = (
        cropped_alpha.astype(np.float32)
        / 255.0
    )

    alpha_float = alpha_float[:, :, None]

    composited = (
        cropped_rgb.astype(np.float32)
        * alpha_float
        +
        white.astype(np.float32)
        * (1 - alpha_float)
    )

    composited = np.clip(
        composited,
        0,
        255
    ).astype(np.uint8)

    # ---------------------------------------------------------
    # 7. Convert to grayscale
    # ---------------------------------------------------------

    gray = cv2.cvtColor(
        composited,
        cv2.COLOR_RGB2GRAY
    )

    # ---------------------------------------------------------
    # 8. Improve contrast
    # ---------------------------------------------------------

    print("Improving contrast...")

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    # ---------------------------------------------------------
    # 9. Save
    # ---------------------------------------------------------

    result = Image.fromarray(
        enhanced
    )

    result.save(
        output_path
    )

    temp_path.unlink(
        missing_ok=True
    )

    print()
    print("Done!")
    print(
        f"Created: {output_path}"
    )


if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "Usage:"
        )

        print(
            "python scripts/prep_photo.py "
            "assets/profile.jpg "
            "source-prepped.png"
        )

        sys.exit(1)

    prepare_photo(
        sys.argv[1],
        sys.argv[2]
    )
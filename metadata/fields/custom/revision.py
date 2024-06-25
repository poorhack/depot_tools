#!/usr/bin/env python3
# Copyright 2024 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
import re
import sys
from typing import Optional

_THIS_DIR = os.path.abspath(os.path.dirname(__file__))
# The repo's root directory.
_ROOT_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", ".."))

# Add the repo's root directory for clearer imports.
sys.path.insert(0, _ROOT_DIR)

import metadata.fields.field_types as field_types
import metadata.fields.custom.version as version_field
import metadata.fields.util as util
import metadata.validation_result as vr


class RevisionField(field_types.SingleLineTextField):
    """Custom field for the revision."""

    def __init__(self):
        super().__init__(name="Revision")
        self._hex_pattern = re.compile(r"^[a-fA-F0-9]{7,40}$")

    def narrow_type(self, value: str) -> Optional[str]:
        value = super().narrow_type(value)
        if not value:
            return None

        if version_field.version_is_unknown(value):
            return None

        if util.is_known_invalid_value(value):
            return None

        if self._hex_pattern.match(value):
            return None

        return value

    def validate(self, value: str) -> Optional[vr.ValidationResult]:
        """Validates the revision string.

        Checks:
          - Non-empty value.
          - Valid hexadecimal format (length 7-40 characters).
          - Preference for "N/A" over "0" for unknown versions.
        """

        if util.is_empty(value):
            return vr.ValidationError(
                reason=f"{self._name} is empty.",
                additional=[
                    "Set this field to 'N/A' if this package does not version "
                    "or is versioned by date or revision.",
                ],
            )

        if value == "0" or util.is_unknown(value):
            return vr.ValidationWarning(
                reason=f"{self._name} is '{value}'.",
                additional=[
                    "Set this field to 'N/A' if this package does not version "
                    "or is versioned by date or revision.",
                ],
            )

        if not self._hex_pattern.match(value):
            return vr.ValidationError(
                reason=
                f"{self._name} '{value}' is not a valid hexadecimal revision.",
                additional=[
                    "Revisions must be hexadecimal strings with a length of 7 to 40 characters."
                ],
            )

        return None  # Valid revision

/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.facebook.buck.rules.coercer;

import com.facebook.buck.core.cell.CellPathResolver;
import com.facebook.buck.core.model.TargetConfiguration;
import com.facebook.buck.core.path.ForwardRelativePath;
import com.facebook.buck.io.filesystem.ProjectFilesystem;
import com.google.common.reflect.TypeToken;

public class IdentityTypeCoercer<T> extends LeafTypeCoercer<T> {
  private TypeToken<T> type;

  public IdentityTypeCoercer(TypeToken<T> type) {
    this.type = type;
  }

  public IdentityTypeCoercer(Class<T> type) {
    this(TypeToken.of(type));
  }

  @Override
  public TypeToken<T> getOutputType() {
    return type;
  }

  @SuppressWarnings("unchecked")
  @Override
  public T coerce(
      CellPathResolver cellRoots,
      ProjectFilesystem filesystem,
      ForwardRelativePath pathRelativeToProjectRoot,
      TargetConfiguration targetConfiguration,
      TargetConfiguration hostConfiguration,
      Object object)
      throws CoerceFailedException {
    if (type.getRawType().isAssignableFrom(object.getClass())) {
      return (T) type.getRawType().cast(object);
    }
    throw CoerceFailedException.simple(object, getOutputType());
  }
}

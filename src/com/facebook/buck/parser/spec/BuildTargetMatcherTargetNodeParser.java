/*
 * Copyright 2015-present Facebook, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License. You may obtain
 * a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

package com.facebook.buck.parser.spec;

import com.facebook.buck.core.model.CanonicalCellName;
import com.facebook.buck.core.model.UnconfiguredBuildTargetView;
import com.facebook.buck.core.parser.buildtargetparser.BuildTargetMatcherParser;
import java.nio.file.Path;

/** Parses a string to {@link TargetNodeSpec} */
public class BuildTargetMatcherTargetNodeParser extends BuildTargetMatcherParser<TargetNodeSpec> {

  @Override
  public TargetNodeSpec createForDescendants(
      CanonicalCellName cellName, Path cellPath, Path basePath) {
    return ImmutableTargetNodePredicateSpec.of(BuildFileSpec.fromRecursivePath(basePath, cellPath));
  }

  @Override
  public TargetNodeSpec createForChildren(
      CanonicalCellName cellName, Path cellPath, Path basePath) {
    return ImmutableTargetNodePredicateSpec.of(BuildFileSpec.fromPath(basePath, cellPath));
  }

  @Override
  public TargetNodeSpec createForSingleton(UnconfiguredBuildTargetView target) {
    return BuildTargetSpec.from(target);
  }
}
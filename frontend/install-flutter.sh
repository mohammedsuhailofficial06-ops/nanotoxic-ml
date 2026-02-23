!/bin/bash

# 1. Clone Flutter stable branch
git clone https://github.com/flutter/flutter.git -b stable --depth 1

# 2. Add Flutter to the PATH
export PATH="$PATH:pwd/flutter/bin"

# 3. Pre-download the artifacts
flutter doctor
flutter config --enable-web

# 4. Run the build
flutter build web --release
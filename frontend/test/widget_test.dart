import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/main.dart';

void main() {
  testWidgets('Portal Loads Test', (WidgetTester tester) async {
    // Just verify the app starts without crashing
    await tester.pumpWidget(NanoToxApp());
  });
}
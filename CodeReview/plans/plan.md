

审查目标：
1. 检查目录 GameScripts/UI
2. 查找所有使用 itemPool.Pop<SkinUIItem>() 或类似方法获取对象的代码
3. 检查每个 Pop 调用是否有对应的 Push 释放

   检查清单：
   - [ ] Pop 的对象创建的时候需要查看调用栈，调用栈基类为UIWindowEx或者FlexItem或者EffectiveListItem
   - [ ] 如果调用栈为UIWindowEx，请检查OnClearWidgets或者OnClose有没有在对应的调用关系链上释放itemPool.Push(m_skinUIItem);
   




请审查 GameScripts/UI 中所有代码的对象池使用情况，检查是否存在内存泄漏：

审查规则：
1. 搜索所有 itemPool.Pop<SkinUIItem>  调用
2. 根据基类类型检查释放逻辑：
   - UIWindowEx：必须在 OnClearWidgets 或 OnClose 中调用 Push 释放
   - FlexItem：必须在 OnClear 或者OnClearWidgets中调用 Push 释放  
   - EffectiveListItem：必须在 OnClear或者OnClearWidgets 中调用 Push 释放
   - Widget/Component：如果在MonoBehaviour/FlexItem/EffectiveListItem使用，必须在生命周期方法中调用组件的释放方法
3. 检查调用链：如果 Pop 在子方法或 Widget 组件中，追踪调用链确保顶层有释放

特殊场景：
- 如果 Pop 在 Widget/Component或者不是UIWindowEx/FlexItem/EffectiveListItem 中，检查使用该组件的 UIWindowEx/FlexItem/EffectiveListItem 是否调用了组件的清理方法
- 如果 Pop 在条件分支中，检查所有分支是否都有对应的 Push
- 忽略注释掉的 Pop 调用

输出格式：
- 发现的问题（CRITICAL/WARNING 级别）
- 问题所在文件、行号、类型
- Pop/Push 调用的具体位置
- 正确的修复建议（包含代码示例）
- 统计数据（总 Pop 数、有问题数、正确数）


比如在UISelectPet.cs文件中 EffList_PetItem类中有个类型为PetItemBigWidget 的成员变量petBigItem_Pet的成员变量，EffList_PetItem中的UpdateData的方法调用了itemPool.Pop<SkinUIItem>() ，但是EffList_PetItem类中并没有在OnClose 或者OnClearWidgets 来调用push

findstr /S /N /I /C:"Pop<SkinUIItem>" *.cs

请审查 GameScripts/UI 中所有文件中代码的对象池使用情况，检查是否存在内存泄漏：
审查规则：
1. 搜索所有 匹配引号内完整字符串"Pop<SkinUIItem>"的调用
2. 根据1调用的赋值给某个成员变量，如果该成员变量是基类为UIWindowEx/FlexItem/EffectiveListItem 的成员变量，记录成员变量所在文件、行号

输出：
- 输出审查规则为2的记录,输出要支持中文



请根据前面的输出 做进一步代码审查
审查规则
1. 根据2的输出的成员所在的类，检查OnClose或者OnClear或者OnClearWidgets 中调用 Push 释放（类似itemPool.Push(m_skinUIItem);）

输出
- 每个文件的检查记录
- 没有进行释放的类的记录 文件 变量名



请审查 GameScripts/UI 中所有文件中代码的对象池使用情况，检查是否存在内存泄漏：
审查规则：
1. 搜索所有 匹配引号内完整字符串"Pop<SkinUIItem>"的调用
2. 根据1调用的赋值给某个成员变量，如果该成员变量是基类为UIWindowEx/FlexItem/EffectiveListItem 的成员变量，记录成员变量所在文件、行号, 成员所在类的类名

输出：
- 输出审查规则为2的记录,输出要支持中文
- 根据2的输出的成员所在的类，检查OnClose或者OnClear或者OnClearWidgets 中调用 Push 释放（类似itemPool.Push(m_skinUIItem);），没有进行Push释放的记录下来


请审查 GameScripts/UI 中所有文件中代码的对象池使用情况，检查是否存在内存泄漏：

审查规则：
1. 搜索所有匹配引号内完整字符串"Pop<SkinUIItem>"的调用
2. 根据1调用的赋值给某个成员变量，如果该成员变量是基类为UIWindowEx/FlexItem/EffectiveListItem 的成员变量，记录成员变量所在文件、行号, 成员所在类的类名

输出：
- 输出审查规则为2的记录,输出要支持中文
- 根据2的输出的成员所在的类，**逐个文件读取完整代码**，检查OnClose或者OnClear或者OnClearWidgets中是否调用Push释放（类似itemPool.Push(m_skinUIItem);）
- **特别注意：即使有UnloadXXX方法存在，也要检查该方法是否在OnClose/OnClear/OnClearWidgets中被实际调用，如果被注释掉则视为未释放**
- **检查清理方法内是否有注释掉的释放代码（以//开头的行）**
- 没有进行Push释放的记录下来，标注问题原因（未调用、被注释、未定义清理方法等）





请审查 GameScripts/UI 中所有文件中代码的对象池使用情况，检查是否存在内存泄漏：

审查规则：
1. 搜索所有匹配引号内完整字符串"Pop<SkinUIItem>"的调用
2. 根据1调用的赋值给某个成员变量，如果该成员变量是基类为UIWindowEx/FlexItem/EffectiveListItem 的成员变量，记录成员变量所在文件、行号, 成员所在类的类名

输出：
- 输出审查规则为2的记录,输出要支持中文
- 根据2的输出的成员所在的类，**逐个文件读取完整代码**，检查OnClose或者OnClear或者OnClearWidgets中是否调用Push释放（类似itemPool.Push(m_skinUIItem);）
- **特别注意：即使有UnloadXXX方法存在，也要检查该方法是否在OnClose/OnClear/OnClearWidgets中被实际调用，如果被注释掉则视为未释放**
- **检查清理方法内是否有注释掉的释放代码（以//开头的行）**
- 没有进行Push释放的记录下来，标注问题原因（未调用、被注释、未定义清理方法等）
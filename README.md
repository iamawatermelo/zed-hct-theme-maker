# zed-hct-theme-maker

zed-hct-theme-maker is, surprisingly, a tool to make Zed themes with the
HCT color space.

## Write your own themes
First, [learn KDL](https://kdl.dev/). It'll take you, like, 5 minutes.

Next, write your theme metadata:
```
version 1
name "my theme"
author "me :D"
```

Then, you can write theme variants:
```
variant "my theme dark" {
  appearance "dark"
  
  style {
    editor.foreground h=0 c=90 t=95
    editor.background h=0 c=90 t=5
    // .. and so on
  }
}
```

You can also use tokens, for reusability:
```
token "primary" h=0 c=90

variant "my theme dark" {
  appearance "dark"
  
  style {
    editor.foreground apply="primary" t=95
    editor.background apply="primary" t=5
  }
}
```

Finally, you can also use layers for maximum composability.
```
token "primary" h=0 c=90

layer "dark-tones" {
  token "fg" t=95
  token "bg" t=5
}

layer "light-tones" {
  token "fg" t=5
  token "bg" t=95
}

layer "theme" {
  style {
    // Note that the last token is applied first. So, fg is applied, 
    // then primary. When a token is applied, already set variables
    // won't be overriden.
    editor.foreground apply="primary fg"
    editor.background apply="primary bg"
  }
}

variant "my theme dark" {
  appearance "dark"
  layer "dark-tones"
  layer "theme"
}

variant "my theme light" {
  appearance "dark"
  layer "light-tones"
  layer "theme"
}
```